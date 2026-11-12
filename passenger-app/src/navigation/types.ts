import type { RideBooking, LocationOption } from '../features/booking/data/bookingApi';
import type { SavedPlace } from '../features/home/domain/homeTypes';

export type PassengerStackParamList = {
  Splash: undefined;
  Login: undefined;
  Signup: undefined;
  Faq: undefined;
  Home: undefined;
  Pickup: undefined;
  Destination: undefined;
  SavedPlace: { place: SavedPlace };
  Fare: undefined;
  Booking: { ride: RideBooking };
  Rides: undefined;
  Addresses: undefined;
  Emergency: undefined;
  Support: undefined;
  InstantRide: undefined;
  Outstation: undefined;
  OutstationPickup: undefined;
  OutstationDestination: undefined;
  Notifications: undefined;
  Settings: undefined;
};

export type BookingDraft = { pickup: LocationOption | null; destination: LocationOption | null; categoryId: number | null; outstationPickup: LocationOption | null; outstationDestination: LocationOption | null };
