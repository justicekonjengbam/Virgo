from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.ride_hailing import (
    Driver,
    FareLineItem,
    FareQuote,
    Payment,
    RateCard,
    Rating,
    Ride,
    RideCategory,
    RideDispatchOffer,
    RideEvent,
)
from app.models.user import Passenger
from app.schemas.booking import (
    DriverActiveRideResponse,
    FareSummaryItemResponse,
    RideMutationResponse,
    RideRatingResponse,
    RideSummaryResponse,
)
from app.services.fare_calculation_service import FareCalculationService
from app.services.realtime_events import publish_driver_ride_event, publish_passenger_status


ACTIVE_STATUSES = ('requested', 'searching', 'driver_assigned', 'driver_arriving', 'driver_arrived', 'in_progress')
PASSENGER_CANCEL_REASONS = {'changed_plans', 'driver_delay', 'wrong_pickup', 'safety_concern', 'emergency', 'other'}
DRIVER_CANCEL_REASONS = {'vehicle_issue', 'passenger_no_show', 'safety_concern', 'emergency', 'other'}


class RideLifecycleService:
    def passenger_active(self, db: Session, passenger: Passenger) -> Ride | None:
        return db.scalar(
            select(Ride)
            .where(
                Ride.passenger_id == passenger.id,
                Ride.status.in_(ACTIVE_STATUSES),
            )
            .order_by(Ride.requested_at.desc())
        )

    def driver_active(self, db: Session, driver: Driver) -> Ride | None:
        return db.scalar(
            select(Ride)
            .where(
                Ride.driver_id == driver.id,
                Ride.status.in_(ACTIVE_STATUSES),
            )
            .order_by(Ride.requested_at.desc())
        )

    def driver_snapshot(self, db: Session, driver: Driver) -> DriverActiveRideResponse | None:
        ride = self.driver_active(db, driver)
        if not ride:
            return None
        passenger = db.get(Passenger, ride.passenger_id)
        return DriverActiveRideResponse(
            ride_id=ride.id,
            status=ride.status,
            pickup_address=ride.pickup_address,
            destination_address=ride.destination_address,
            pickup_latitude=float(ride.pickup_latitude),
            pickup_longitude=float(ride.pickup_longitude),
            destination_latitude=float(ride.destination_latitude),
            destination_longitude=float(ride.destination_longitude),
            passenger_name=passenger.full_name if passenger else 'Passenger',
            route_geojson=ride.route_geojson,
            can_cancel=ride.status in {'driver_arriving', 'driver_arrived'},
            can_end=ride.status == 'in_progress',
        )

    def cancel_by_passenger(self, db: Session, passenger: Passenger, ride_id: int, reason: str, confirm: bool) -> RideMutationResponse:
        ride = db.scalar(select(Ride).where(Ride.id == ride_id, Ride.passenger_id == passenger.id))
        if not ride:
            raise HTTPException(status_code=404, detail='Ride was not found.')
        if not confirm:
            raise HTTPException(status_code=400, detail='Confirm cancellation before ending this ride.')
        if ride.status not in ACTIVE_STATUSES:
            raise HTTPException(status_code=409, detail='This ride is no longer active.')
        if reason not in PASSENGER_CANCEL_REASONS:
            raise HTTPException(status_code=422, detail='Choose a valid passenger cancellation reason.')
        if ride.status == 'in_progress' and reason not in {'safety_concern', 'emergency'}:
            raise HTTPException(status_code=409, detail='An in-progress ride can only be ended for safety or an emergency. Contact support for other issues.')
        event = 'trip_ended_by_passenger' if ride.status == 'in_progress' else 'ride_cancelled_by_passenger'
        self._cancel(db, ride, 'passenger', reason, event, passenger.id)
        return RideMutationResponse(ride_id=ride.id, status=ride.status, message='Your ride has been ended.' if event.startswith('trip_ended') else 'Your ride has been cancelled.')

    def cancel_by_driver(self, db: Session, driver: Driver, ride_id: int, reason: str, confirm: bool) -> RideMutationResponse:
        ride = db.scalar(select(Ride).where(Ride.id == ride_id, Ride.driver_id == driver.id))
        if not ride:
            raise HTTPException(status_code=404, detail='Active ride was not found.')
        if not confirm:
            raise HTTPException(status_code=400, detail='Confirm before ending this ride.')
        if ride.status not in {'driver_arriving', 'driver_arrived', 'in_progress'}:
            raise HTTPException(status_code=409, detail='This ride cannot be ended from its current state.')
        if reason not in DRIVER_CANCEL_REASONS:
            raise HTTPException(status_code=422, detail='Choose a valid Driver cancellation reason.')
        if ride.status == 'in_progress' and reason not in {'vehicle_issue', 'safety_concern', 'emergency'}:
            raise HTTPException(status_code=409, detail='An in-progress ride can only be ended for a vehicle issue, safety concern, or emergency.')
        event = 'trip_ended_by_driver' if ride.status == 'in_progress' else 'ride_cancelled_by_driver'
        self._cancel(db, ride, 'driver', reason, event, driver.id)
        return RideMutationResponse(ride_id=ride.id, status=ride.status, message='The ride has been ended and the passenger was notified.')

    def action(
        self,
        db: Session,
        driver: Driver,
        ride_id: int,
        action: str,
        start_otp: str | None = None,
        payment_method: str | None = 'cash',
    ) -> RideMutationResponse:
        ride = db.scalar(select(Ride).where(Ride.id == ride_id, Ride.driver_id == driver.id))
        if not ride:
            raise HTTPException(status_code=404, detail='Active ride was not found.')

        # Payment confirmation flow for completed ride
        if action == 'confirm_payment':
            if ride.status != 'completed':
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Payment can only be confirmed after ride completion.')
            payment = db.scalar(select(Payment).where(Payment.ride_id == ride.id).limit(1))
            now = datetime.now(UTC)
            if payment:
                payment.status = 'completed'
                payment.method = payment_method or payment.method or 'cash'
            else:
                quote = db.scalar(select(FareQuote).where(FareQuote.ride_id == ride.id, FareQuote.is_final.is_(True)).order_by(FareQuote.created_at.desc()))
                amount = quote.amount_paise if quote else 0
                payment = Payment(
                    ride_id=ride.id,
                    amount_paise=amount,
                    currency='INR',
                    method=payment_method or 'cash',
                    status='completed',
                    idempotency_key=f'ride_{ride.id}_pay_{int(now.timestamp())}',
                )
                db.add(payment)
            db.add(RideEvent(ride_id=ride.id, actor_type='driver', actor_id=driver.id, event_type='payment_confirmed', payload={'method': payment_method}))
            db.commit()
            return RideMutationResponse(ride_id=ride.id, status=ride.status, message='Payment collection confirmed successfully.')

        transitions = {
            ('driver_arriving', 'arrived'): ('driver_arrived', 'Driver reached pickup'),
            ('driver_arrived', 'start'): ('in_progress', 'Trip started'),
            ('in_progress', 'complete'): ('completed', 'Trip completed'),
        }
        transition = transitions.get((ride.status, action))
        if not transition:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='This ride action is not available right now.')

        now = datetime.now(UTC)

        if action == 'arrived':
            ride.arrived_at = now

        elif action == 'start':
            if (ride.otp_attempts or 0) >= 5:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Too many incorrect OTP attempts. For passenger security, ride start is locked. Please contact support.',
                )
            if not start_otp or not self.verify_ride_otp(start_otp, ride.otp_salt, ride.start_otp_hash):
                ride.otp_attempts = (ride.otp_attempts or 0) + 1
                db.commit()
                remaining = max(0, 5 - ride.otp_attempts)
                message = (
                    f'The ride-start OTP is incorrect. Ask the passenger for the 4-digit OTP shown in their app. Attempts remaining: {remaining}.'
                    if remaining > 0
                    else 'Too many incorrect OTP attempts. For passenger security, ride start is locked. Please contact support.'
                )
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)

            ride.started_at = now
            if ride.arrived_at:
                elapsed_waiting_seconds = max(0.0, (now - self._aware(ride.arrived_at)).total_seconds())
                ride.actual_waiting_minutes = round(elapsed_waiting_seconds / 60.0, 2)
            else:
                ride.actual_waiting_minutes = 0.0

        elif action == 'complete':
            ride.completed_at = now
            ride.final_distance_meters = ride.final_distance_meters or ride.estimated_distance_meters or 1000
            ride.final_duration_seconds = max(1, round((now - self._aware(ride.started_at or now)).total_seconds()))

            # Recalculate final fare using the FareCalculationService
            category = db.get(RideCategory, ride.category_id)
            if not category:
                raise HTTPException(status_code=404, detail='Category not found.')

            rate_card = db.scalar(
                select(RateCard).where(
                    RateCard.category_code == category.code,
                    RateCard.version == (ride.rate_card_version or 1),
                )
            ) or FareCalculationService.get_active_rate_card(db, category.code)

            dist_km = max(0.1, round((ride.final_distance_meters or 1000) / 1000.0, 1))
            breakdown = FareCalculationService.calculate_fare(
                category_code=category.code,
                distance_km=dist_km,
                waiting_minutes=ride.actual_waiting_minutes or 0.0,
                rate_card=rate_card,
                pickup_coords=(float(ride.pickup_latitude), float(ride.pickup_longitude)),
                dest_coords=(float(ride.destination_latitude), float(ride.destination_longitude)),
            )

            quote = db.scalar(select(FareQuote).where(FareQuote.ride_id == ride.id).order_by(FareQuote.created_at.desc()))
            if not quote:
                quote = FareQuote(ride_id=ride.id, amount_paise=breakdown.customer_pays_paise, is_final=True)
                db.add(quote)
                db.flush()

            quote.amount_paise = breakdown.customer_pays_paise
            quote.is_final = True
            quote.rate_card_version = breakdown.rate_card_version
            quote.base_fare_paise = breakdown.base_fare_paise
            quote.distance_fare_paise = breakdown.distance_fare_paise
            quote.waiting_charge_paise = breakdown.waiting_charge_paise
            quote.surcharge_paise = breakdown.surcharge_paise
            quote.subtotal_paise = breakdown.gross_fare_paise
            quote.discount_paise = breakdown.discount_paise
            quote.gst_paise = breakdown.gst_paise
            quote.commission_paise = breakdown.commission_paise
            quote.driver_net_paise = breakdown.driver_net_paise

            # Replace line items with final breakdown
            existing_items = db.scalars(select(FareLineItem).where(FareLineItem.fare_quote_id == quote.id)).all()
            for item in existing_items:
                db.delete(item)
            db.flush()

            final_items = [
                FareLineItem(fare_quote_id=quote.id, item_type='base_fare', amount_paise=breakdown.base_fare_paise),
                FareLineItem(fare_quote_id=quote.id, item_type='distance_fare', amount_paise=breakdown.distance_fare_paise),
            ]
            if breakdown.waiting_charge_paise > 0:
                final_items.append(FareLineItem(fare_quote_id=quote.id, item_type='waiting_charge', amount_paise=breakdown.waiting_charge_paise))
            if breakdown.surcharge_paise > 0:
                final_items.append(FareLineItem(fare_quote_id=quote.id, item_type='surcharge', amount_paise=breakdown.surcharge_paise))
            final_items.append(FareLineItem(fare_quote_id=quote.id, item_type='gst', amount_paise=breakdown.gst_paise))
            db.add_all(final_items)

            # Record pending payment
            existing_payment = db.scalar(select(Payment).where(Payment.ride_id == ride.id).limit(1))
            if not existing_payment:
                db.add(
                    Payment(
                        ride_id=ride.id,
                        amount_paise=breakdown.customer_pays_paise,
                        currency='INR',
                        method=payment_method or 'cash',
                        status='pending_collection',
                        idempotency_key=f'ride_{ride.id}_pay_{int(now.timestamp())}',
                    )
                )

            driver.completed_rides_count += 1

        ride.status = transition[0]
        db.add(RideEvent(ride_id=ride.id, actor_type='driver', actor_id=driver.id, event_type=f'ride_{action}', payload=None))
        db.commit()
        db.refresh(ride)

        publish_passenger_status(db, ride)
        publish_driver_ride_event(driver.id, ride, f'ride.{ride.status}')
        return RideMutationResponse(ride_id=ride.id, status=ride.status, message=transition[1])

    def summary(self, db: Session, ride: Ride, rater_type: str) -> RideSummaryResponse:
        if ride.status != 'completed':
            raise HTTPException(status_code=409, detail='Fare summary is available after ride completion.')
        quote = db.scalar(select(FareQuote).where(FareQuote.ride_id == ride.id, FareQuote.is_final.is_(True)).order_by(FareQuote.created_at.desc()))
        items = db.scalars(select(FareLineItem).where(FareLineItem.fare_quote_id == quote.id).order_by(FareLineItem.id)).all() if quote else []
        ratings = set(db.scalars(select(Rating.rater_type).where(Rating.ride_id == ride.id)).all())
        payment = db.scalar(select(Payment).where(Payment.ride_id == ride.id).limit(1))

        return RideSummaryResponse(
            ride_id=ride.id,
            status=ride.status,
            pickup_address=ride.pickup_address,
            destination_address=ride.destination_address,
            distance_km=round((ride.final_distance_meters or ride.estimated_distance_meters or 0) / 1000, 1),
            duration_minutes=max(1, round((ride.final_duration_seconds or ride.estimated_duration_seconds or 0) / 60)),
            fare_paise=quote.amount_paise if quote else 0,
            commission_paise=quote.commission_paise if quote else None,
            driver_net_paise=quote.driver_net_paise if quote else None,
            waiting_charge_paise=quote.waiting_charge_paise if quote else None,
            payment_status=payment.status if payment else 'pending_collection',
            payment_method=payment.method if payment else 'cash',
            fare_items=[FareSummaryItemResponse(label=item.item_type.replace('_', ' ').title(), amount_paise=item.amount_paise) for item in items],
            passenger_rating_submitted='passenger' in ratings,
            driver_rating_submitted='driver' in ratings,
        )

    def rate(self, db: Session, ride: Ride, rater_type: str, score: int, comment: str | None) -> RideRatingResponse:
        if ride.status != 'completed':
            raise HTTPException(status_code=409, detail='Ratings are available after ride completion.')
        if db.scalar(select(Rating).where(Rating.ride_id == ride.id, Rating.rater_type == rater_type)):
            raise HTTPException(status_code=409, detail='You already rated this ride.')
        db.add(Rating(ride_id=ride.id, rater_type=rater_type, score=score, comment=comment.strip() if comment else None))
        db.flush()
        if rater_type == 'passenger' and ride.driver_id:
            values = db.scalars(select(Rating.score).join(Ride, Ride.id == Rating.ride_id).where(Rating.rater_type == 'passenger', Ride.driver_id == ride.driver_id)).all()
            driver = db.get(Driver, ride.driver_id)
            if driver and values:
                driver.rating_average = round(sum(values) / len(values), 2)
        db.commit()
        return RideRatingResponse(ride_id=ride.id, score=score, message='Thank you. Your rating was submitted.')

    @classmethod
    def create_ride_otp_credentials(cls, secret_key: str, ride_id: int, passenger_id: int) -> tuple[str, str]:
        salt = secrets.token_hex(16)
        message = f'ride_otp:{ride_id}:{passenger_id}:{salt}'.encode()
        digest = hmac.new(secret_key.encode(), message, hashlib.sha256).hexdigest()
        otp = f'{int(digest[:8], 16) % 10000:04d}'
        otp_hash = hashlib.sha256(f'{otp}:{salt}'.encode()).hexdigest()
        return salt, otp_hash

    @classmethod
    def recover_ride_otp(cls, secret_key: str, ride_id: int, passenger_id: int, salt: str | None, expected_hash: str | None) -> str | None:
        if not salt or not expected_hash:
            return None
        message = f'ride_otp:{ride_id}:{passenger_id}:{salt}'.encode()
        digest = hmac.new(secret_key.encode(), message, hashlib.sha256).hexdigest()
        otp = f'{int(digest[:8], 16) % 10000:04d}'
        computed_hash = hashlib.sha256(f'{otp}:{salt}'.encode()).hexdigest()
        if secrets.compare_digest(computed_hash, expected_hash):
            return otp
        return None

    @classmethod
    def verify_ride_otp(cls, entered_otp: str | None, salt: str | None, expected_hash: str | None) -> bool:
        if not entered_otp or not salt or not expected_hash:
            return False
        cleaned = entered_otp.strip()
        if len(cleaned) != 4 or not cleaned.isdigit():
            return False
        computed_hash = hashlib.sha256(f'{cleaned}:{salt}'.encode()).hexdigest()
        return secrets.compare_digest(computed_hash, expected_hash)

    @classmethod
    def get_passenger_ride_otp(cls, db: Session, ride: Ride) -> str | None:
        settings = get_settings()
        if not ride.otp_salt or not ride.start_otp_hash:
            salt, otp_hash = cls.create_ride_otp_credentials(
                settings.jwt_secret_key, ride.id, ride.passenger_id
            )
            ride.otp_salt = salt
            ride.start_otp_hash = otp_hash
            ride.otp_attempts = 0
            db.commit()
            db.refresh(ride)
        return cls.recover_ride_otp(
            settings.jwt_secret_key,
            ride.id,
            ride.passenger_id,
            ride.otp_salt,
            ride.start_otp_hash,
        )

    @staticmethod
    def _cancel(db: Session, ride: Ride, actor: str, reason: str, event: str, actor_id: int) -> None:
        driver_id = ride.driver_id
        previous_status = ride.status
        ride.status, ride.cancelled_at = 'cancelled', datetime.now(UTC)
        ride.cancelled_by, ride.cancellation_reason = actor, reason.strip()
        db.add(RideEvent(ride_id=ride.id, actor_type=actor, actor_id=actor_id, event_type=event, payload={'reason': reason.strip()}))
        pending = db.scalars(select(RideDispatchOffer).where(RideDispatchOffer.ride_id == ride.id, RideDispatchOffer.status == 'pending')).all()
        for offer in pending:
            offer.status, offer.responded_at = 'cancelled', datetime.now(UTC)

        # Cancellation fee calculation
        category = db.get(RideCategory, ride.category_id)
        if category:
            cancelled_after_arrival = (previous_status == 'driver_arrived' or reason == 'passenger_no_show')
            rate_card = FareCalculationService.get_active_rate_card(db, category.code)
            fee = FareCalculationService.calculate_cancellation_fee(
                category.code,
                cancelled_after_arrival=cancelled_after_arrival,
                rate_card=rate_card,
            )
            if fee > 0:
                quote = db.scalar(select(FareQuote).where(FareQuote.ride_id == ride.id).order_by(FareQuote.created_at.desc()))
                if not quote:
                    quote = FareQuote(ride_id=ride.id, amount_paise=fee, is_final=True)
                    db.add(quote)
                    db.flush()
                else:
                    quote.amount_paise = fee
                    quote.is_final = True
                db.add(FareLineItem(fare_quote_id=quote.id, item_type='cancellation_fee', amount_paise=fee))

        db.commit()
        db.refresh(ride)
        publish_passenger_status(db, ride)
        if driver_id:
            publish_driver_ride_event(driver_id, ride, 'ride.cancelled')

    @staticmethod
    def _aware(value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value
