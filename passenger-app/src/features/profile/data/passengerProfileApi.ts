import { apiClient } from '../../../services/apiClient';

export type PassengerProfile = { full_name: string; phone_number: string; email: string | null; preferred_language: string };
export const passengerProfileApi = {
  get: async () => (await apiClient.get<PassengerProfile>('/api/v1/passengers/me/profile')).data,
  update: async (payload: Partial<Pick<PassengerProfile, 'full_name' | 'email' | 'preferred_language'>>) => (await apiClient.patch<PassengerProfile>('/api/v1/passengers/me/profile', payload)).data,
};
