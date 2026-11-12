import { apiClient } from '../../../services/apiClient';
import type { LocationOption } from '../../booking/data/bookingApi';

export type OutstationBooking = { id: number; scheduled_at: string; pickup_address: string; destination_address: string; preferred_vehicle_type: string | null; status: string; estimated_distance_km: number | null; estimated_fare_paise: number | null; support_note: string | null; driver_name: string | null; driver_phone_number: string | null; vehicle_name: string | null; vehicle_registration_number: string | null; can_cancel: boolean; created_at: string };
export type OutstationBookingInput = { scheduled_at: string; pickup: LocationOption; destination: LocationOption; preferred_vehicle_type: 'sedan' | 'suv' | 'muv' | null };
export type OutstationEstimate = { distance_km:number; duration_minutes:number; estimated_fare_paise:number; route_geojson:GeoJSON.Geometry; disclaimer:string };
const payload = (input: OutstationBookingInput) => ({ ...input, pickup: { ...input.pickup, place_id: input.pickup.place_id ?? `catalog:${input.pickup.id}` }, destination: { ...input.destination, place_id: input.destination.place_id ?? `catalog:${input.destination.id}` } });

export const outstationService = {
  list: async () => (await apiClient.get<OutstationBooking[]>('/api/v1/passengers/me/outstation-bookings')).data,
  create: async (input: OutstationBookingInput) => (await apiClient.post<OutstationBooking>('/api/v1/passengers/me/outstation-bookings', payload(input))).data,
  estimate: async (input: OutstationBookingInput) => (await apiClient.post<OutstationEstimate>('/api/v1/passengers/me/outstation-estimates', payload(input))).data,
  cancel: async (id: number, reason: string) => (await apiClient.post<OutstationBooking>(`/api/v1/passengers/me/outstation-bookings/${id}/cancel`, { reason })).data,
};
