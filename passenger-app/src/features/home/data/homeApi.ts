import { apiClient } from '../../../services/apiClient';
import type { PassengerHome } from '../domain/homeTypes';

export const homeApi = {
  async getHome(): Promise<PassengerHome> {
    const response = await apiClient.get<PassengerHome>('/api/v1/passengers/me/home');
    return response.data;
  },
};
