import { apiClient } from '../../../services/apiClient';

export type DriverProfile = { full_name: string; phone_number: string; operating_city: string | null; onboarding_completed: boolean; status: string };

export const driverProfileService = {
  async get(): Promise<DriverProfile> {
    const response = await apiClient.get<DriverProfile>('/api/v1/auth/drivers/me');
    return response.data;
  },
  async update(payload: Pick<DriverProfile, 'full_name' | 'operating_city'>): Promise<DriverProfile> {
    const response = await apiClient.patch<DriverProfile>('/api/v1/auth/drivers/me', payload);
    return response.data;
  },
};
