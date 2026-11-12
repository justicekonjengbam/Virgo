from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ride_hailing import RateCard, RideCategory

IMPHAL_CENTER_LAT = 24.8170
IMPHAL_CENTER_LON = 93.9368


@dataclass(frozen=True)
class FareBreakdown:
    category_code: str
    rate_card_version: int
    distance_km: float
    waiting_minutes: float
    billable_waiting_minutes: float
    base_fare_paise: int
    first_tier_km: float
    first_tier_rate_paise: int
    second_tier_rate_paise: int
    distance_fare_paise: int
    waiting_charge_per_minute_paise: int
    waiting_charge_paise: int
    is_surcharge: bool
    surcharge_percentage: float
    surcharge_paise: int
    gross_fare_paise: int
    discount_paise: int
    fare_after_discount_paise: int
    gst_rate: float
    gst_paise: int
    total_exact_paise: int
    customer_pays_paise: int
    commission_rate: float
    commission_paise: int
    driver_net_paise: int
    cancellation_fee_paise: int


class FareCalculationService:
    """Virgo Happy Cabbing fare engine implementing exact specification formulas."""

    DEFAULT_RATE_CARDS = {
        'hatchback': {
            'base_fare_paise': 8000,
            'first_tier_km': 6.0,
            'first_tier_rate_paise': 2800,
            'second_tier_rate_paise': 2900,
            'waiting_charge_per_minute_paise': 200,
            'waiting_grace_period_minutes': 3,
            'surcharge_distance_threshold_km': 12.0,
            'surcharge_percentage': 0.15,
            'cancellation_fee_paise': 10000,
            'gst_rate': 0.05,
            'commission_rate': 0.10,
        },
        'sedan': {
            'base_fare_paise': 9000,
            'first_tier_km': 6.0,
            'first_tier_rate_paise': 2800,
            'second_tier_rate_paise': 2900,
            'waiting_charge_per_minute_paise': 200,
            'waiting_grace_period_minutes': 3,
            'surcharge_distance_threshold_km': 12.0,
            'surcharge_percentage': 0.15,
            'cancellation_fee_paise': 10000,
            'gst_rate': 0.05,
            'commission_rate': 0.10,
        },
        'suv': {
            'base_fare_paise': 12000,
            'first_tier_km': 6.0,
            'first_tier_rate_paise': 3000,
            'second_tier_rate_paise': 3100,
            'waiting_charge_per_minute_paise': 300,
            'waiting_grace_period_minutes': 3,
            'surcharge_distance_threshold_km': 12.0,
            'surcharge_percentage': 0.15,
            'cancellation_fee_paise': 10000,
            'gst_rate': 0.05,
            'commission_rate': 0.10,
        },
        'e_auto': {
            'base_fare_paise': 3500,
            'first_tier_km': 6.0,
            'first_tier_rate_paise': 2000,
            'second_tier_rate_paise': 2100,
            'waiting_charge_per_minute_paise': 150,
            'waiting_grace_period_minutes': 3,
            'surcharge_distance_threshold_km': 12.0,
            'surcharge_percentage': 0.15,
            'cancellation_fee_paise': 0,
            'gst_rate': 0.05,
            'commission_rate': 0.10,
        },
        'e_rickshaw': {
            'base_fare_paise': 3500,
            'first_tier_km': 6.0,
            'first_tier_rate_paise': 2000,
            'second_tier_rate_paise': 2100,
            'waiting_charge_per_minute_paise': 150,
            'waiting_grace_period_minutes': 3,
            'surcharge_distance_threshold_km': 12.0,
            'surcharge_percentage': 0.15,
            'cancellation_fee_paise': 0,
            'gst_rate': 0.05,
            'commission_rate': 0.10,
        },
        'bike': {
            'base_fare_paise': 1500,
            'first_tier_km': 6.0,
            'first_tier_rate_paise': 1300,
            'second_tier_rate_paise': 1400,
            'waiting_charge_per_minute_paise': 150,
            'waiting_grace_period_minutes': 3,
            'surcharge_distance_threshold_km': 12.0,
            'surcharge_percentage': 0.15,
            'cancellation_fee_paise': 0,
            'gst_rate': 0.05,
            'commission_rate': 0.10,
        },
    }

    # Backward compatibility aliases
    CODE_ALIASES = {
        'car': 'hatchback',
        'auto': 'e_auto',
    }

    @classmethod
    def normalize_code(cls, category_code: str) -> str:
        code = category_code.lower().strip()
        return cls.CODE_ALIASES.get(code, code)

    @classmethod
    def get_active_rate_card(cls, db: Session, category_code: str) -> RateCard | None:
        normalized = cls.normalize_code(category_code)
        card = db.scalar(
            select(RateCard)
            .where(RateCard.category_code == normalized, RateCard.is_active.is_(True))
            .order_by(RateCard.version.desc())
        )
        if not card and normalized != category_code:
            card = db.scalar(
                select(RateCard)
                .where(RateCard.category_code == category_code, RateCard.is_active.is_(True))
                .order_by(RateCard.version.desc())
            )
        return card

    @classmethod
    def haversine_distance_km(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 6371 * 2 * asin(sqrt(a))

    @classmethod
    def is_center_distance_surcharge(
        cls,
        pickup_lat: float | None = None,
        pickup_lon: float | None = None,
        dest_lat: float | None = None,
        dest_lon: float | None = None,
        threshold_km: float = 12.0,
    ) -> bool:
        if pickup_lat is not None and pickup_lon is not None:
            if cls.haversine_distance_km(pickup_lat, pickup_lon, IMPHAL_CENTER_LAT, IMPHAL_CENTER_LON) > threshold_km:
                return True
        if dest_lat is not None and dest_lon is not None:
            if cls.haversine_distance_km(dest_lat, dest_lon, IMPHAL_CENTER_LAT, IMPHAL_CENTER_LON) > threshold_km:
                return True
        return False

    @classmethod
    def calculate_fare(
        cls,
        category_code: str,
        distance_km: float,
        waiting_minutes: float = 0.0,
        is_surcharge: bool = False,
        promo_discount_paise: int = 0,
        rate_card: RateCard | None = None,
        pickup_coords: tuple[float, float] | None = None,
        dest_coords: tuple[float, float] | None = None,
    ) -> FareBreakdown:
        normalized_code = cls.normalize_code(category_code)
        defaults = cls.DEFAULT_RATE_CARDS.get(normalized_code, cls.DEFAULT_RATE_CARDS['hatchback'])

        version = rate_card.version if rate_card else 1
        base_fare_paise = rate_card.base_fare_paise if rate_card else defaults['base_fare_paise']
        first_tier_km = rate_card.first_tier_km if rate_card else defaults['first_tier_km']
        first_tier_rate_paise = rate_card.first_tier_rate_paise if rate_card else defaults['first_tier_rate_paise']
        second_tier_rate_paise = rate_card.second_tier_rate_paise if rate_card else defaults['second_tier_rate_paise']
        waiting_charge_per_minute_paise = (
            rate_card.waiting_charge_per_minute_paise if rate_card else defaults['waiting_charge_per_minute_paise']
        )
        waiting_grace_period_minutes = (
            rate_card.waiting_grace_period_minutes if rate_card else defaults['waiting_grace_period_minutes']
        )
        surcharge_threshold_km = (
            rate_card.surcharge_distance_threshold_km if rate_card else defaults['surcharge_distance_threshold_km']
        )
        surcharge_percentage = rate_card.surcharge_percentage if rate_card else defaults['surcharge_percentage']
        cancellation_fee_paise = rate_card.cancellation_fee_paise if rate_card else defaults['cancellation_fee_paise']
        gst_rate = rate_card.gst_rate if rate_card else defaults['gst_rate']
        commission_rate = rate_card.commission_rate if rate_card else defaults['commission_rate']

        # 1. Tiered distance calculation:
        # Distance = min(dist, 6) * tier1 + max(dist - 6, 0) * tier2
        tier1_dist = min(max(0.0, float(distance_km)), float(first_tier_km))
        tier2_dist = max(0.0, float(distance_km) - float(first_tier_km))
        distance_fare_paise = round(tier1_dist * first_tier_rate_paise + tier2_dist * second_tier_rate_paise)

        # 2. Waiting charges calculation:
        # Waiting charges: Waiting Rate * max(waiting_mins - grace_period_mins, 0)
        billable_waiting_minutes = max(0.0, float(waiting_minutes) - float(waiting_grace_period_minutes))
        waiting_charge_paise = round(billable_waiting_minutes * waiting_charge_per_minute_paise)

        # Subtotal before surcharge: Base + Distance + Waiting
        subtotal_before_surcharge = base_fare_paise + distance_fare_paise + waiting_charge_paise

        # 3. Surcharge check:
        # Distance > 12km OR pickup/drop > 12km from Imphal center OR explicit is_surcharge
        has_surcharge = is_surcharge or (distance_km > surcharge_threshold_km)
        if not has_surcharge and (pickup_coords or dest_coords):
            has_surcharge = cls.is_center_distance_surcharge(
                pickup_lat=pickup_coords[0] if pickup_coords else None,
                pickup_lon=pickup_coords[1] if pickup_coords else None,
                dest_lat=dest_coords[0] if dest_coords else None,
                dest_lon=dest_coords[1] if dest_coords else None,
                threshold_km=surcharge_threshold_km,
            )

        surcharge_paise = round(subtotal_before_surcharge * surcharge_percentage) if has_surcharge else 0

        # Gross fare before promo
        gross_fare_paise = subtotal_before_surcharge + surcharge_paise

        # 4. Promo discount
        discount_paise = max(0, min(promo_discount_paise, gross_fare_paise))
        fare_after_discount_paise = gross_fare_paise - discount_paise

        # 5. GST (5% of Fare after discount)
        gst_paise = round(fare_after_discount_paise * gst_rate)

        # 6. Customer Pays: round(Fare + GST) to nearest rupee (nearest 100 paise)
        total_exact_paise = fare_after_discount_paise + gst_paise
        customer_pays_rupees = round(total_exact_paise / 100.0)
        customer_pays_paise = int(customer_pays_rupees * 100)

        # 7. Commission: 10% of Fare before promo
        commission_paise = round(gross_fare_paise * commission_rate)

        # 8. Driver Net: (Fare before promo) - Commission
        driver_net_paise = gross_fare_paise - commission_paise

        return FareBreakdown(
            category_code=normalized_code,
            rate_card_version=version,
            distance_km=float(distance_km),
            waiting_minutes=float(waiting_minutes),
            billable_waiting_minutes=billable_waiting_minutes,
            base_fare_paise=base_fare_paise,
            first_tier_km=first_tier_km,
            first_tier_rate_paise=first_tier_rate_paise,
            second_tier_rate_paise=second_tier_rate_paise,
            distance_fare_paise=distance_fare_paise,
            waiting_charge_per_minute_paise=waiting_charge_per_minute_paise,
            waiting_charge_paise=waiting_charge_paise,
            is_surcharge=has_surcharge,
            surcharge_percentage=surcharge_percentage,
            surcharge_paise=surcharge_paise,
            gross_fare_paise=gross_fare_paise,
            discount_paise=discount_paise,
            fare_after_discount_paise=fare_after_discount_paise,
            gst_rate=gst_rate,
            gst_paise=gst_paise,
            total_exact_paise=total_exact_paise,
            customer_pays_paise=customer_pays_paise,
            commission_rate=commission_rate,
            commission_paise=commission_paise,
            driver_net_paise=driver_net_paise,
            cancellation_fee_paise=cancellation_fee_paise,
        )

    @classmethod
    def calculate_cancellation_fee(
        cls,
        category_code: str,
        cancelled_after_arrival: bool = True,
        rate_card: RateCard | None = None,
    ) -> int:
        if not cancelled_after_arrival:
            return 0
        normalized = cls.normalize_code(category_code)
        if rate_card:
            return rate_card.cancellation_fee_paise
        defaults = cls.DEFAULT_RATE_CARDS.get(normalized, cls.DEFAULT_RATE_CARDS['hatchback'])
        return defaults['cancellation_fee_paise']

