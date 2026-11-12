import { apiClient } from '../../../services/apiClient';

export type DriverRideRequest = { pickup_address: string; destination_address: string; estimated_distance_km: number; expected_fare_paise: number; pickup_minutes_away: number };
export type DriverTrip = { id: number; pickup_address: string; destination_address: string; category: string; completed_at: string | null; fare_paise: number };
export type DriverSupportArticle = { id: string; title: string; body: string };

export const driverMenuService = {
  async getRideRequest(): Promise<DriverRideRequest> { return (await apiClient.get<DriverRideRequest>('/api/v1/drivers/menu/ride-request')).data; },
  async getTripHistory(): Promise<DriverTrip[]> { return (await apiClient.get<DriverTrip[]>('/api/v1/drivers/menu/trip-history')).data; },
  async getSupport(): Promise<DriverSupportArticle[]> { return (await apiClient.get<DriverSupportArticle[]>('/api/v1/drivers/menu/support')).data; },
};
