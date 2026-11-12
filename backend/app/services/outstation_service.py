from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ride_hailing import Driver, DriverVehicleAssignment, Notification, OutstationBooking, Vehicle
from app.models.user import Passenger
from app.schemas.outstation import AdminOutstationUpdate, DriverOutstationAssignmentResponse, EligibleOutstationDriverResponse, OutstationBookingCreate, OutstationBookingResponse, OutstationEstimateResponse
from app.services.map_provider_service import MapProviderService
from app.services.realtime_events import publish_outstation_assignment, publish_outstation_update


OPEN_STATUSES = ('requested', 'confirmed', 'driver_assigned')


class OutstationService:
    def __init__(self, map_provider: MapProviderService | None = None) -> None:
        self.map_provider = map_provider or MapProviderService()

    def estimate(self, request: OutstationBookingCreate) -> OutstationEstimateResponse:
        scheduled = self._aware(request.scheduled_at)
        now = datetime.now(UTC)
        if scheduled < now + timedelta(hours=4) or scheduled > now + timedelta(days=180):
            raise HTTPException(status_code=422, detail='Choose a departure between 4 hours and 180 days from now.')
        if request.pickup.place_id == request.destination.place_id:
            raise HTTPException(status_code=422, detail='Pickup and destination must be different.')
        route = self.map_provider.route((request.pickup.latitude, request.pickup.longitude), (request.destination.latitude, request.destination.longitude))
        distance_km = round(route.distance_meters / 1000, 1)
        if distance_km < 150:
            raise HTTPException(status_code=422, detail='This route is below 150 km. Use regular ride booking for this journey.')
        return OutstationEstimateResponse(distance_km=distance_km, duration_minutes=max(1, round(route.duration_seconds / 60)), estimated_fare_paise=self._fare(distance_km, request.preferred_vehicle_type, scheduled), route_geojson=route.geometry)

    def create(self, db: Session, passenger: Passenger, request: OutstationBookingCreate) -> OutstationBookingResponse:
        scheduled = self._aware(request.scheduled_at)
        now = datetime.now(UTC)
        if scheduled < now + timedelta(hours=4):
            raise HTTPException(status_code=422, detail='Outstation rides must be requested at least 4 hours in advance.')
        if scheduled > now + timedelta(days=180):
            raise HTTPException(status_code=422, detail='Outstation rides can be requested up to 180 days in advance.')
        if request.pickup.place_id == request.destination.place_id:
            raise HTTPException(status_code=422, detail='Pickup and destination must be different.')
        estimate = self.estimate(request)
        open_count = db.scalar(select(func.count()).select_from(OutstationBooking).where(OutstationBooking.passenger_id == passenger.id, OutstationBooking.status.in_(OPEN_STATUSES))) or 0
        if open_count >= 3:
            raise HTTPException(status_code=409, detail='You can keep up to 3 active outstation requests. Contact support to change an existing request.')
        duplicate = db.scalar(select(OutstationBooking.id).where(OutstationBooking.passenger_id == passenger.id, OutstationBooking.status.in_(OPEN_STATUSES), OutstationBooking.scheduled_at == scheduled, OutstationBooking.pickup_place_id == request.pickup.place_id, OutstationBooking.destination_place_id == request.destination.place_id))
        if duplicate:
            raise HTTPException(status_code=409, detail='This outstation request has already been submitted.')
        booking = OutstationBooking(passenger_id=passenger.id, scheduled_at=scheduled, pickup_address=request.pickup.formatted_address, pickup_place_id=request.pickup.place_id, pickup_latitude=request.pickup.latitude, pickup_longitude=request.pickup.longitude, destination_address=request.destination.formatted_address, destination_place_id=request.destination.place_id, destination_latitude=request.destination.latitude, destination_longitude=request.destination.longitude, preferred_vehicle_type=request.preferred_vehicle_type, status='requested', estimated_distance_km=Decimal(str(estimate.distance_km)), estimated_fare_paise=estimate.estimated_fare_paise, route_geojson=estimate.route_geojson)
        db.add(booking); db.flush()
        self._notify(db, passenger.id, 'outstation_requested', 'Outstation request received', f'Our support team will review booking #{booking.id} and confirm the fare.', booking.id)
        db.commit(); db.refresh(booking)
        return self._response(db, booking)

    def passenger_list(self, db: Session, passenger: Passenger) -> list[OutstationBookingResponse]:
        items = db.scalars(select(OutstationBooking).where(OutstationBooking.passenger_id == passenger.id).order_by(OutstationBooking.scheduled_at.desc())).all()
        return [self._response(db, item) for item in items]

    def cancel(self, db: Session, passenger: Passenger, booking_id: int, reason: str) -> OutstationBookingResponse:
        booking = db.scalar(select(OutstationBooking).where(OutstationBooking.id == booking_id, OutstationBooking.passenger_id == passenger.id))
        if not booking:
            raise HTTPException(status_code=404, detail='Outstation booking was not found.')
        if booking.status not in OPEN_STATUSES:
            raise HTTPException(status_code=409, detail='This outstation booking can no longer be cancelled.')
        hours_remaining = (self._aware(booking.scheduled_at) - datetime.now(UTC)).total_seconds() / 3600
        cutoff = 24 if booking.status == 'driver_assigned' else 6
        if hours_remaining < cutoff:
            raise HTTPException(status_code=409, detail=f'Please contact support to cancel within {cutoff} hours of departure.')
        booking.status = 'cancelled'; booking.cancelled_at = datetime.now(UTC); booking.cancellation_reason = reason.strip()
        self._notify(db, passenger.id, 'outstation_cancelled', 'Outstation booking cancelled', f'Booking #{booking.id} has been cancelled.', booking.id)
        db.commit(); db.refresh(booking)
        return self._response(db, booking)

    def admin_list(self, db: Session, status_filter: str | None) -> list[OutstationBookingResponse]:
        query = select(OutstationBooking).order_by(OutstationBooking.scheduled_at.asc())
        if status_filter:
            query = query.where(OutstationBooking.status == status_filter)
        return [self._response(db, item) for item in db.scalars(query).all()]

    def eligible_drivers(self, db: Session, booking_id: int) -> list[EligibleOutstationDriverResponse]:
        booking = db.get(OutstationBooking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail='Outstation booking was not found.')
        if booking.status != 'confirmed':
            raise HTTPException(status_code=409, detail='Confirm this booking before selecting a driver.')
        conflict_ids = select(OutstationBooking.driver_id).where(
            OutstationBooking.driver_id.is_not(None),
            OutstationBooking.status == 'driver_assigned',
            OutstationBooking.scheduled_at.between(booking.scheduled_at - timedelta(hours=12), booking.scheduled_at + timedelta(hours=12)),
            OutstationBooking.id != booking.id,
        )
        rows = db.execute(
            select(Driver, Vehicle)
            .join(DriverVehicleAssignment, DriverVehicleAssignment.driver_id == Driver.id)
            .join(Vehicle, Vehicle.id == DriverVehicleAssignment.vehicle_id)
            .where(
                Driver.status == 'active',
                Vehicle.verification_status == 'verified',
                DriverVehicleAssignment.ended_at.is_(None),
                Driver.id.not_in(conflict_ids),
            )
            .order_by(Driver.rating_average.desc(), Driver.completed_rides_count.desc(), Driver.full_name)
        ).all()
        return [EligibleOutstationDriverResponse(
            full_name=driver.full_name,
            phone_number=self._local_phone(driver.phone_number),
            operating_city=driver.operating_city,
            rating=float(driver.rating_average),
            completed_rides=driver.completed_rides_count,
            vehicle_name=f'{vehicle.make} {vehicle.model}',
            vehicle_registration_number=vehicle.registration_number,
            vehicle_category=vehicle.category_code,
            seat_count=vehicle.seat_count,
        ) for driver, vehicle in rows]

    def admin_update(self, db: Session, booking_id: int, request: AdminOutstationUpdate, admin_id: int) -> OutstationBookingResponse:
        booking = db.get(OutstationBooking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail='Outstation booking was not found.')
        now = datetime.now(UTC)
        if request.status == 'confirmed':
            if booking.status != 'requested':
                raise HTTPException(status_code=409, detail='Only a requested booking can be confirmed.')
            distance = request.estimated_distance_km or float(booking.estimated_distance_km or 0)
            if distance < 150:
                raise HTTPException(status_code=422, detail='Outstation distance must be at least 150 km.')
            booking.estimated_distance_km = Decimal(str(distance)); booking.estimated_fare_paise = self._fare(distance, booking.preferred_vehicle_type, booking.scheduled_at); booking.confirmed_at = now
        elif request.status == 'driver_assigned':
            if booking.status != 'confirmed' or not request.driver_phone_number:
                raise HTTPException(status_code=409, detail='Confirm the fare before assigning a driver.')
            local_phone = request.driver_phone_number
            driver = db.scalar(select(Driver).where(Driver.phone_number.in_((local_phone, f'91{local_phone}', f'+91{local_phone}'))))
            if not driver:
                raise HTTPException(status_code=404, detail='No driver account matches this mobile number.')
            assignment = db.scalar(select(DriverVehicleAssignment).where(DriverVehicleAssignment.driver_id == driver.id, DriverVehicleAssignment.ended_at.is_(None)).order_by(DriverVehicleAssignment.started_at.desc()))
            vehicle = db.get(Vehicle, assignment.vehicle_id) if assignment else None
            if not driver or driver.status != 'active' or not vehicle or vehicle.verification_status != 'verified':
                raise HTTPException(status_code=409, detail='Assign an active driver with a verified vehicle.')
            conflict = db.scalar(select(OutstationBooking.id).where(OutstationBooking.driver_id == driver.id, OutstationBooking.status == 'driver_assigned', OutstationBooking.scheduled_at.between(booking.scheduled_at - timedelta(hours=12), booking.scheduled_at + timedelta(hours=12)), OutstationBooking.id != booking.id))
            if conflict:
                raise HTTPException(status_code=409, detail='This driver already has an outstation assignment near the selected time.')
            booking.driver_id = driver.id; booking.vehicle_id = vehicle.id; booking.assigned_at = now
        elif request.status in {'rejected', 'cancelled'}:
            if not (request.support_note or '').strip():
                raise HTTPException(status_code=422, detail='Add a reason before rejecting or cancelling the booking.')
            booking.cancelled_at = now; booking.cancellation_reason = request.support_note.strip()
        elif request.status == 'completed' and booking.status != 'driver_assigned':
            raise HTTPException(status_code=409, detail='Only an assigned outstation booking can be completed.')
        booking.status = request.status; booking.support_note = request.support_note.strip() if request.support_note else booking.support_note; booking.assigned_admin_id = admin_id
        title, body = self._notification_copy(booking)
        self._notify(db, booking.passenger_id, f'outstation_{booking.status}', title, body, booking.id)
        db.commit(); db.refresh(booking)
        if booking.status == 'driver_assigned' and booking.driver_id:
            publish_outstation_assignment(booking.driver_id, booking.id, self._aware(booking.scheduled_at))
        elif booking.driver_id:
            publish_outstation_update(booking.driver_id, booking.id, booking.status)
        return self._response(db, booking)

    def driver_assignments(self, db: Session, driver: Driver) -> list[DriverOutstationAssignmentResponse]:
        bookings = db.scalars(select(OutstationBooking).where(OutstationBooking.driver_id == driver.id, OutstationBooking.status.in_(('driver_assigned', 'completed')), OutstationBooking.scheduled_at >= datetime.now(UTC) - timedelta(days=90)).order_by(OutstationBooking.status.desc(), OutstationBooking.scheduled_at)).all()
        result = []
        for booking in bookings:
            passenger, vehicle = db.get(Passenger, booking.passenger_id), db.get(Vehicle, booking.vehicle_id)
            if passenger and vehicle:
                result.append(DriverOutstationAssignmentResponse(id=booking.id, status=booking.status, scheduled_at=booking.scheduled_at, pickup_address=booking.pickup_address, destination_address=booking.destination_address, passenger_name=passenger.full_name, passenger_phone_number=self._local_phone(passenger.phone_number), estimated_distance_km=float(booking.estimated_distance_km or 0), estimated_fare_paise=booking.estimated_fare_paise or 0, vehicle_name=f'{vehicle.make} {vehicle.model}', vehicle_registration_number=vehicle.registration_number))
        return result

    def _response(self, db: Session, booking: OutstationBooking) -> OutstationBookingResponse:
        passenger = db.get(Passenger, booking.passenger_id)
        driver, vehicle = db.get(Driver, booking.driver_id) if booking.driver_id else None, db.get(Vehicle, booking.vehicle_id) if booking.vehicle_id else None
        hours_remaining = (self._aware(booking.scheduled_at) - datetime.now(UTC)).total_seconds() / 3600
        cutoff = 24 if booking.status == 'driver_assigned' else 6
        return OutstationBookingResponse(id=booking.id, scheduled_at=booking.scheduled_at, pickup_address=booking.pickup_address, destination_address=booking.destination_address, preferred_vehicle_type=booking.preferred_vehicle_type, status=booking.status, estimated_distance_km=float(booking.estimated_distance_km) if booking.estimated_distance_km is not None else None, estimated_fare_paise=booking.estimated_fare_paise, support_note=booking.support_note, driver_name=driver.full_name if driver else None, driver_phone_number=self._local_phone(driver.phone_number) if driver else None, vehicle_name=f'{vehicle.make} {vehicle.model}' if vehicle else None, vehicle_registration_number=vehicle.registration_number if vehicle else None, can_cancel=booking.status in OPEN_STATUSES and hours_remaining >= cutoff, created_at=booking.created_at, passenger_name=passenger.full_name if passenger else 'Passenger', passenger_phone_number=self._local_phone(passenger.phone_number) if passenger else '', pickup_latitude=float(booking.pickup_latitude) if booking.pickup_latitude is not None else None, pickup_longitude=float(booking.pickup_longitude) if booking.pickup_longitude is not None else None, destination_latitude=float(booking.destination_latitude) if booking.destination_latitude is not None else None, destination_longitude=float(booking.destination_longitude) if booking.destination_longitude is not None else None, route_geojson=booking.route_geojson)

    @staticmethod
    def _fare(distance_km: float, preference: str | None, scheduled_at: datetime) -> int:
        option = preference or 'sedan'; base, per_extra_km = {'sedan': (250000, 1600), 'suv': (330000, 2200), 'muv': (360000, 2400)}[option]
        fare = base + max(0, round(distance_km - 150)) * per_extra_km + 50000
        if OutstationService._aware(scheduled_at).hour < 6 or OutstationService._aware(scheduled_at).hour >= 21:
            fare = round(fare * 1.15)
        return fare

    @staticmethod
    def _notify(db: Session, passenger_id: int, kind: str, title: str, body: str, booking_id: int) -> None:
        db.add(Notification(passenger_id=passenger_id, notification_type=kind, title=title, body=body, data_json={'outstation_booking_id': booking_id}))

    @staticmethod
    def _notification_copy(booking: OutstationBooking) -> tuple[str, str]:
        if booking.status == 'confirmed': return 'Outstation fare confirmed', f'Booking #{booking.id} is confirmed at ₹{(booking.estimated_fare_paise or 0) / 100:,.0f}. Driver assignment is next.'
        if booking.status == 'driver_assigned': return 'Driver assigned', f'Your driver has been assigned for outstation booking #{booking.id}.'
        if booking.status == 'completed': return 'Outstation ride completed', f'Booking #{booking.id} is marked complete.'
        return 'Outstation request updated', f'Booking #{booking.id} was {booking.status}. {booking.support_note or ""}'.strip()

    @staticmethod
    def _aware(value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)

    @staticmethod
    def _local_phone(value: str) -> str:
        digits = ''.join(character for character in value if character.isdigit())
        return digits[-10:]
