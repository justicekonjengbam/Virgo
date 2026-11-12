"""Importing this package registers every model with SQLAlchemy metadata."""

from app.models.ride_hailing import (  # noqa: F401
    AuditLog, DeviceSession, Driver, DriverCurrentLocation, DriverDocument,
    DriverVehicleAssignment, EmergencyContact, FareLineItem, FareQuote,
    LocationCatalog, Notification, OutboxEvent, OutstationBooking, PassengerProfile, Payment, Rating, Ride,
    RideCategory, RideDispatchOffer, RideEvent, RideStop, SavedPlace, ServiceArea, SupportTicket,
    Vehicle,
)
from app.models.user import AdminUser, Passenger  # noqa: F401
