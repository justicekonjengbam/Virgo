import { apiClient } from '../../../services/apiClient';
import type { GeolocationPosition } from '@maplibre/maplibre-react-native';

export type DriverRideOffer = { offer_id: number; ride_id: number; pickup_address: string; destination_address: string; estimated_distance_km: number; expected_fare_paise: number; pickup_minutes_away: number; expires_at: string; pickup_latitude: number; pickup_longitude: number; destination_latitude: number; destination_longitude: number };
export type RideOfferResponse = { ride_id: number; ride_status: string; message: string };
export type DriverActiveRide = { ride_id: number; status: string; pickup_address: string; destination_address: string; pickup_latitude: number; pickup_longitude: number; destination_latitude: number; destination_longitude: number; passenger_name: string; route_geojson: GeoJSON.Geometry | null; can_cancel: boolean; can_end: boolean };
export type RideSummary = {
  ride_id: number;
  status: string;
  pickup_address: string;
  destination_address: string;
  distance_km: number;
  duration_minutes: number;
  fare_paise: number;
  commission_paise?: number;
  driver_net_paise?: number;
  waiting_charge_paise?: number;
  payment_status?: string;
  payment_method?: string;
  fare_items: { label: string; amount_paise: number }[];
  passenger_rating_submitted: boolean;
  driver_rating_submitted: boolean;
};
export type DriverOutstationAssignment = { id: number; status: 'driver_assigned' | 'completed'; scheduled_at: string; pickup_address: string; destination_address: string; passenger_name: string; passenger_phone_number: string; estimated_distance_km: number; estimated_fare_paise: number; vehicle_name: string; vehicle_registration_number: string };

export const rideMatchingService = {
  getCurrentOffer: async () => (await apiClient.get<DriverRideOffer | null>('/api/v1/drivers/me/ride-offers/current')).data,
  respond: async (offerId: number, decision: 'accepted' | 'declined') => (await apiClient.post<RideOfferResponse>(`/api/v1/drivers/me/ride-offers/${offerId}/response`, { decision })).data,
  activeRide: async () => (await apiClient.get<DriverActiveRide | null>('/api/v1/drivers/me/rides/active')).data,
  updateLocation: async (position: GeolocationPosition) => apiClient.put('/api/v1/drivers/me/location', { latitude: position.coords.latitude, longitude: position.coords.longitude, heading_degrees: position.coords.heading == null ? null : Math.round(position.coords.heading), accuracy_meters: position.coords.accuracy, speed_mps: position.coords.speed, recorded_at: new Date(position.timestamp).toISOString() }),
  action: async (rideId: number, action: 'arrived' | 'start' | 'complete' | 'confirm_payment', startOtp?: string, paymentMethod: string = 'cash') => (await apiClient.post(`/api/v1/drivers/me/rides/${rideId}/actions`, { action, start_otp: startOtp, payment_method: paymentMethod })).data,
  cancel: async (rideId: number, reason: string) => (await apiClient.post(`/api/v1/drivers/me/rides/${rideId}/cancel`, { reason, confirm: true })).data,
  summary: async (rideId: number) => (await apiClient.get<RideSummary>(`/api/v1/drivers/me/rides/${rideId}/summary`)).data,
  rate: async (rideId: number, score: number, comment?: string) => (await apiClient.post(`/api/v1/drivers/me/rides/${rideId}/rating`, { score, comment })).data,
  outstationAssignments: async () => (await apiClient.get<DriverOutstationAssignment[]>('/api/v1/drivers/me/outstation-assignments')).data,
};
