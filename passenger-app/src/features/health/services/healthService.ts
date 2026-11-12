import { apiClient } from '../../../services/apiClient';

export type HealthStatus = {
  status: string;
  version: string;
  environment: string;
};

export const healthService = {
  async check(): Promise<HealthStatus> {
    const response = await apiClient.get<HealthStatus>('/health');
    return response.data;
  },
};
