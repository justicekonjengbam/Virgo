import { apiClient } from '../../../services/apiClient';

export type MapConfiguration = { style_url: string; attribution: string; service_area: number[]; service_center: number[]; service_radius_km: number };
let cachedConfig: MapConfiguration | null = null;

export async function getMapConfiguration(): Promise<MapConfiguration> {
  if (!cachedConfig) cachedConfig = (await apiClient.get<MapConfiguration>('/api/v1/maps/config')).data;
  return cachedConfig;
}
