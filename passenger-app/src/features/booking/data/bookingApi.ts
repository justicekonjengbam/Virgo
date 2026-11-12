import { apiClient } from '../../../services/apiClient';

export type LocationOption = { id?: number | null; place_id?: string | null; name: string; formatted_address: string; latitude: number; longitude: number };
export type FareEstimate = { pickup: LocationOption; destination: LocationOption; category_name: string; distance_km: number; duration_minutes: number; fare_paise: number; fare_items: { label: string; amount_paise: number }[]; route_geojson?: GeoJSON.Geometry | null };
export type RideBooking = { ride_id: number; status: string; pickup_address: string; destination_address: string; fare_paise: number; requested_at: string; message: string };
export type RideStatus = { ride_id: number; status: string; message: string; pickup_address: string; destination_address: string; fare_paise: number; driver_name: string | null; vehicle_name: string | null; vehicle_registration_number: string | null; driver_arrival_minutes: number | null; pickup_latitude: number; pickup_longitude: number; destination_latitude: number; destination_longitude: number; driver_latitude: number | null; driver_longitude: number | null; driver_heading_degrees: number | null; route_geojson: GeoJSON.Geometry | null; can_cancel: boolean; can_end: boolean; ride_start_otp: string | null; cancellation_reason: string | null };
export type RideSummary = { ride_id: number; status: string; pickup_address: string; destination_address: string; distance_km: number; duration_minutes: number; fare_paise: number; fare_items: { label: string; amount_paise: number }[]; passenger_rating_submitted: boolean; driver_rating_submitted: boolean };

const placePayload = (place: LocationOption) => ({ place_id: place.place_id ?? `catalog:${place.id}`, name: place.name, formatted_address: place.formatted_address, latitude: place.latitude, longitude: place.longitude });
const ridePayload = (pickup: LocationOption, destination: LocationOption, categoryId: number) => ({ pickup: placePayload(pickup), destination: placePayload(destination), category_id: categoryId });

export const bookingApi = {
  locations: async () => (await apiClient.get<LocationOption[]>('/api/v1/passengers/me/locations')).data,
  estimate: async (pickup: LocationOption, destination: LocationOption, categoryId: number) => (await apiClient.post<FareEstimate>('/api/v1/passengers/me/ride-estimates', ridePayload(pickup, destination, categoryId))).data,
  book: async (pickup: LocationOption, destination: LocationOption, categoryId: number) => (await apiClient.post<RideBooking>('/api/v1/passengers/me/rides', ridePayload(pickup, destination, categoryId))).data,
  status: async (rideId: number) => (await apiClient.get<RideStatus>(`/api/v1/passengers/me/rides/${rideId}/status`)).data,
  activeRide: async () => (await apiClient.get<RideStatus | null>('/api/v1/passengers/me/rides/active/current')).data,
  cancel: async (rideId: number, reason: string) => (await apiClient.post(`/api/v1/passengers/me/rides/${rideId}/cancel`, { reason, confirm: true })).data,
  summary: async (rideId: number) => (await apiClient.get<RideSummary>(`/api/v1/passengers/me/rides/${rideId}/summary`)).data,
  rate: async (rideId: number, score: number, comment?: string) => (await apiClient.post(`/api/v1/passengers/me/rides/${rideId}/rating`, { score, comment })).data,
  updateSavedPlace: async (savedPlaceId: number, location: LocationOption) => (await apiClient.patch(`/api/v1/passengers/me/saved-places/${savedPlaceId}`, { location: placePayload(location) })).data,
};
