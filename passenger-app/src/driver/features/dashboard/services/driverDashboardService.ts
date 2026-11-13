import { apiClient } from '../../../services/apiClient';

export type DriverVehicleStatus = {
  category: string;
  make: string;
  model: string;
  registration_number: string;
  seat_count: number;
  color: string | null;
  verification_status: 'pending' | 'verified' | 'rejected' | 'expired';
};

export type DriverDashboard = {
  full_name: string;
  is_online: boolean;
  online_minutes: number;
  safety_score: number | null;
  rating: number | null;
  today_earnings_paise: number;
  month_earnings_paise: number;
  today_completed_rides: number;
  month_completed_rides: number;
  vehicle: DriverVehicleStatus | null;
};

export const driverDashboardService = {
  async getDashboard(): Promise<DriverDashboard> {
    const response = await apiClient.get<DriverDashboard>('/api/v1/drivers/dashboard');
    return response.data;
  },

  async updateAvailability(isOnline: boolean): Promise<DriverDashboard> {
    const response = await apiClient.put<DriverDashboard>('/api/v1/drivers/dashboard/availability', { is_online: isOnline });
    return response.data;
  },
};
