from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.ride_hailing import (
    Driver,
    DriverDocument,
    FareQuote,
    Payment,
    RateCard,
    Ride,
    RideCategory,
    RideEvent,
    SupportTicket,
    Vehicle,
)
from app.models.user import Passenger
from app.repositories.driver_repository import DriverRepository
from app.schemas.admin import (
    AdminDriverDocumentResponse,
    AdminDriverResponse,
    AdminRateCardResponse,
    AdminRateCardUpdateRequest,
    AdminRideDetailResponse,
    AdminRideEventResponse,
    AdminRideListItemResponse,
    AdminSupportTicketResponse,
    AdminSupportTicketUpdate,
)
from app.services.realtime_events import publish_passenger_status, publish_driver_ride_event


class AdminOperationsService:
    def __init__(self, driver_repository: DriverRepository | None = None) -> None:
        self.driver_repository = driver_repository or DriverRepository()

    def documents(self, db: Session, review_status: str | None) -> list[AdminDriverDocumentResponse]:
        query = select(DriverDocument, Driver).join(Driver, DriverDocument.driver_id == Driver.id).order_by(DriverDocument.created_at.asc())
        if review_status:
            query = query.where(DriverDocument.verification_status == review_status)
        items: list[AdminDriverDocumentResponse] = []
        for document, driver in db.execute(query).all():
            vehicle = self.driver_repository.get_active_vehicle(db, driver.id)
            items.append(AdminDriverDocumentResponse(
                driver_id=driver.id, driver_name=driver.full_name, operating_city=driver.operating_city,
                vehicle_registration_number=vehicle.registration_number if vehicle else None,
                document_type=document.document_type, document_number=document.document_number,
                verification_status=document.verification_status, review_note=document.review_note,
                created_at=document.created_at,
            ))
        return items

    def drivers(self, db: Session, driver_status: str | None) -> list[AdminDriverResponse]:
        query = select(Driver).order_by(Driver.created_at.desc())
        if driver_status:
            query = query.where(Driver.status == driver_status)
        results: list[AdminDriverResponse] = []
        for driver in db.scalars(query).all():
            vehicle = self.driver_repository.get_active_vehicle(db, driver.id)
            documents = self.driver_repository.get_documents(db, driver.id)
            results.append(AdminDriverResponse(
                id=driver.id, full_name=driver.full_name, phone_number=driver.phone_number,
                operating_city=driver.operating_city, status=driver.status,
                vehicle_category=vehicle.category_code if vehicle else None,
                vehicle_name=f'{vehicle.make} {vehicle.model}' if vehicle else None,
                vehicle_registration_number=vehicle.registration_number if vehicle else None,
                vehicle_verification_status=vehicle.verification_status if vehicle else None,
                document_statuses={document.document_type: document.verification_status for document in documents},
            ))
        return results

    def tickets(self, db: Session, ticket_status: str | None) -> list[AdminSupportTicketResponse]:
        query = select(SupportTicket, Passenger).join(Passenger, SupportTicket.passenger_id == Passenger.id).order_by(SupportTicket.created_at.desc())
        if ticket_status:
            query = query.where(SupportTicket.status == ticket_status)
        return [AdminSupportTicketResponse(
            id=ticket.id, passenger_name=passenger.full_name, category=ticket.category, status=ticket.status,
            subject=ticket.subject, description=ticket.description, created_at=ticket.created_at,
            assigned_admin_id=ticket.assigned_admin_id, resolution_note=ticket.resolution_note,
        ) for ticket, passenger in db.execute(query).all()]

    def update_ticket(self, db: Session, ticket_id: int, request: AdminSupportTicketUpdate, admin_id: int) -> AdminSupportTicketResponse:
        ticket = db.get(SupportTicket, ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Support ticket was not found.')
        ticket.status = request.status
        ticket.assigned_admin_id = admin_id
        ticket.resolution_note = request.resolution_note.strip() if request.resolution_note else None
        ticket.resolved_at = datetime.now(UTC) if request.status in {'resolved', 'closed'} else None
        db.add(ticket)
        db.commit()
        passenger = db.get(Passenger, ticket.passenger_id)
        return AdminSupportTicketResponse(id=ticket.id, passenger_name=passenger.full_name, category=ticket.category, status=ticket.status, subject=ticket.subject, description=ticket.description, created_at=ticket.created_at, assigned_admin_id=ticket.assigned_admin_id, resolution_note=ticket.resolution_note)

    # ==================== Milestone 3: Local Ride Operations ====================

    def rides(self, db: Session, status_filter: str | None = None, search: str | None = None) -> list[AdminRideListItemResponse]:
        query = select(Ride).order_by(Ride.requested_at.desc())
        if status_filter:
            query = query.where(Ride.status == status_filter)

        rides = db.scalars(query).all()
        results: list[AdminRideListItemResponse] = []

        for ride in rides:
            passenger = db.get(Passenger, ride.passenger_id)
            if not passenger:
                continue

            if search:
                term = search.lower()
                matches_search = (
                    term in passenger.full_name.lower()
                    or term in passenger.phone_number
                    or term in ride.pickup_address.lower()
                    or term in ride.destination_address.lower()
                )
                if not matches_search:
                    continue

            driver = db.get(Driver, ride.driver_id) if ride.driver_id else None
            vehicle = db.get(Vehicle, ride.vehicle_id) if ride.vehicle_id else None
            category = db.get(RideCategory, ride.category_id)
            quote = db.scalar(select(FareQuote).where(FareQuote.ride_id == ride.id).order_by(FareQuote.created_at.desc()))
            payment = db.scalar(select(Payment).where(Payment.ride_id == ride.id).limit(1))

            results.append(
                AdminRideListItemResponse(
                    id=ride.id,
                    passenger_id=passenger.id,
                    passenger_name=passenger.full_name,
                    passenger_phone=passenger.phone_number,
                    driver_id=driver.id if driver else None,
                    driver_name=driver.full_name if driver else None,
                    driver_phone=driver.phone_number if driver else None,
                    vehicle_name=f'{vehicle.make} {vehicle.model}' if vehicle else None,
                    vehicle_registration_number=vehicle.registration_number if vehicle else None,
                    category_code=category.code if category else 'unknown',
                    category_name=category.display_name if category else 'Standard',
                    status=ride.status,
                    pickup_address=ride.pickup_address,
                    destination_address=ride.destination_address,
                    fare_paise=quote.amount_paise if quote else 0,
                    payment_status=payment.status if payment else None,
                    requested_at=ride.requested_at,
                    completed_at=ride.completed_at,
                    cancelled_at=ride.cancelled_at,
                )
            )

        return results

    def ride_detail(self, db: Session, ride_id: int) -> AdminRideDetailResponse:
        ride = db.get(Ride, ride_id)
        if not ride:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ride was not found.')

        passenger = db.get(Passenger, ride.passenger_id)
        driver = db.get(Driver, ride.driver_id) if ride.driver_id else None
        vehicle = db.get(Vehicle, ride.vehicle_id) if ride.vehicle_id else None
        category = db.get(RideCategory, ride.category_id)
        quote = db.scalar(select(FareQuote).where(FareQuote.ride_id == ride.id).order_by(FareQuote.created_at.desc()))
        payment = db.scalar(select(Payment).where(Payment.ride_id == ride.id).limit(1))
        events = db.scalars(select(RideEvent).where(RideEvent.ride_id == ride.id).order_by(RideEvent.occurred_at.asc())).all()

        return AdminRideDetailResponse(
            id=ride.id,
            status=ride.status,
            passenger_id=passenger.id if passenger else 0,
            passenger_name=passenger.full_name if passenger else 'Passenger',
            passenger_phone=passenger.phone_number if passenger else '',
            driver_id=driver.id if driver else None,
            driver_name=driver.full_name if driver else None,
            driver_phone=driver.phone_number if driver else None,
            vehicle_id=vehicle.id if vehicle else None,
            vehicle_name=f'{vehicle.make} {vehicle.model}' if vehicle else None,
            vehicle_registration_number=vehicle.registration_number if vehicle else None,
            category_code=category.code if category else 'unknown',
            category_name=category.display_name if category else 'Standard',
            pickup_address=ride.pickup_address,
            pickup_latitude=float(ride.pickup_latitude),
            pickup_longitude=float(ride.pickup_longitude),
            destination_address=ride.destination_address,
            destination_latitude=float(ride.destination_latitude),
            destination_longitude=float(ride.destination_longitude),
            estimated_distance_km=round((ride.estimated_distance_meters or 0) / 1000.0, 1),
            final_distance_km=round((ride.final_distance_meters or 0) / 1000.0, 1) if ride.final_distance_meters else None,
            actual_waiting_minutes=ride.actual_waiting_minutes,
            rate_card_version=ride.rate_card_version,
            requested_at=ride.requested_at,
            accepted_at=ride.accepted_at,
            arrived_at=ride.arrived_at,
            started_at=ride.started_at,
            completed_at=ride.completed_at,
            cancelled_at=ride.cancelled_at,
            cancellation_reason=ride.cancellation_reason,
            cancelled_by=ride.cancelled_by,
            fare_paise=quote.amount_paise if quote else 0,
            base_fare_paise=quote.base_fare_paise if quote else None,
            distance_fare_paise=quote.distance_fare_paise if quote else None,
            waiting_charge_paise=quote.waiting_charge_paise if quote else None,
            surcharge_paise=quote.surcharge_paise if quote else None,
            discount_paise=quote.discount_paise if quote else None,
            gst_paise=quote.gst_paise if quote else None,
            commission_paise=quote.commission_paise if quote else None,
            driver_net_paise=quote.driver_net_paise if quote else None,
            payment_status=payment.status if payment else None,
            payment_method=payment.method if payment else None,
            events=[
                AdminRideEventResponse(
                    id=ev.id,
                    actor_type=ev.actor_type,
                    actor_id=ev.actor_id,
                    event_type=ev.event_type,
                    payload=ev.payload,
                    occurred_at=ev.occurred_at,
                )
                for ev in events
            ],
        )

    def assign_driver(
        self,
        db: Session,
        ride_id: int,
        driver_id: int | None = None,
        driver_phone: str | None = None,
        admin_id: int | None = None,
    ) -> AdminRideDetailResponse:
        ride = db.get(Ride, ride_id)
        if not ride:
            raise HTTPException(status_code=404, detail='Ride was not found.')
        if ride.status not in {'requested', 'searching'}:
            raise HTTPException(status_code=409, detail=f'Cannot assign driver to a ride with status {ride.status}.')

        driver = None
        if driver_id:
            driver = db.get(Driver, driver_id)
        elif driver_phone:
            cleaned = driver_phone.replace(' ', '').replace('-', '')
            driver = db.scalar(
                select(Driver).where(
                    or_(
                        Driver.phone_number == cleaned,
                        Driver.phone_number == f'+91{cleaned[-10:]}',
                        Driver.phone_number.endswith(cleaned[-10:]),
                    )
                )
            )

        if not driver:
            raise HTTPException(status_code=404, detail='Driver was not found.')
        if driver.status != 'active':
            raise HTTPException(status_code=409, detail=f'Driver {driver.full_name} is not active (status: {driver.status}).')

        vehicle = self.driver_repository.get_active_vehicle(db, driver.id)
        if not vehicle or vehicle.verification_status != 'verified':
            raise HTTPException(status_code=409, detail=f'Driver {driver.full_name} does not have a verified vehicle.')

        now = datetime.now(UTC)
        ride.driver_id = driver.id
        ride.vehicle_id = vehicle.id
        ride.status = 'driver_arriving'
        ride.accepted_at = now

        db.add(
            RideEvent(
                ride_id=ride.id,
                actor_type='admin',
                actor_id=admin_id,
                event_type='admin_assigned_driver',
                payload={'driver_id': driver.id, 'vehicle_id': vehicle.id},
            )
        )
        db.commit()
        db.refresh(ride)

        publish_passenger_status(db, ride)
        publish_driver_ride_event(driver.id, ride, 'ride.driver_arriving')

        return self.ride_detail(db, ride_id)

    def cancel_ride(self, db: Session, ride_id: int, reason: str, admin_id: int | None = None) -> AdminRideDetailResponse:
        ride = db.get(Ride, ride_id)
        if not ride:
            raise HTTPException(status_code=404, detail='Ride was not found.')
        if ride.status in {'completed', 'cancelled'}:
            raise HTTPException(status_code=409, detail='Ride is already finished.')

        now = datetime.now(UTC)
        driver_id = ride.driver_id
        ride.status = 'cancelled'
        ride.cancelled_by = 'admin'
        ride.cancellation_reason = reason.strip()
        ride.cancelled_at = now

        db.add(
            RideEvent(
                ride_id=ride.id,
                actor_type='admin',
                actor_id=admin_id,
                event_type='admin_cancelled_ride',
                payload={'reason': reason.strip()},
            )
        )
        db.commit()
        db.refresh(ride)

        publish_passenger_status(db, ride)
        if driver_id:
            publish_driver_ride_event(driver_id, ride, 'ride.cancelled')

        return self.ride_detail(db, ride_id)

    # ==================== Milestone 3: Rate Card Management ====================

    def rate_cards(self, db: Session) -> list[AdminRateCardResponse]:
        cards = db.scalars(select(RateCard).order_by(RateCard.category_code, RateCard.version.desc())).all()
        return [
            AdminRateCardResponse(
                id=c.id,
                category_code=c.category_code,
                version=c.version,
                is_active=c.is_active,
                base_fare_paise=c.base_fare_paise,
                first_tier_km=c.first_tier_km,
                first_tier_rate_paise=c.first_tier_rate_paise,
                second_tier_rate_paise=c.second_tier_rate_paise,
                waiting_charge_per_minute_paise=c.waiting_charge_per_minute_paise,
                waiting_grace_period_minutes=c.waiting_grace_period_minutes,
                surcharge_distance_threshold_km=c.surcharge_distance_threshold_km,
                surcharge_percentage=c.surcharge_percentage,
                cancellation_fee_paise=c.cancellation_fee_paise,
                gst_rate=c.gst_rate,
                commission_rate=c.commission_rate,
                updated_at=c.updated_at,
            )
            for c in cards
        ]

    def update_rate_card(
        self,
        db: Session,
        card_id: int,
        request: AdminRateCardUpdateRequest,
        admin_id: int | None = None,
    ) -> AdminRateCardResponse:
        card = db.get(RateCard, card_id)
        if not card:
            raise HTTPException(status_code=404, detail='Rate card was not found.')

        updates = request.model_dump(exclude_unset=True)
        for key, value in updates.items():
            if value is not None:
                setattr(card, key, value)

        card.version += 1
        card.updated_at = datetime.now(UTC)
        db.add(card)
        db.commit()
        db.refresh(card)

        return AdminRateCardResponse(
            id=card.id,
            category_code=card.category_code,
            version=card.version,
            is_active=card.is_active,
            base_fare_paise=card.base_fare_paise,
            first_tier_km=card.first_tier_km,
            first_tier_rate_paise=card.first_tier_rate_paise,
            second_tier_rate_paise=card.second_tier_rate_paise,
            waiting_charge_per_minute_paise=card.waiting_charge_per_minute_paise,
            waiting_grace_period_minutes=card.waiting_grace_period_minutes,
            surcharge_distance_threshold_km=card.surcharge_distance_threshold_km,
            surcharge_percentage=card.surcharge_percentage,
            cancellation_fee_paise=card.cancellation_fee_paise,
            gst_rate=card.gst_rate,
            commission_rate=card.commission_rate,
            updated_at=card.updated_at,
        )
