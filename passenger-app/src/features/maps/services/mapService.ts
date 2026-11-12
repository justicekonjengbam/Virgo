import { apiClient } from '../../../services/apiClient';
import type { LocationOption } from '../../booking/data/bookingApi';

export type MapConfiguration = { style_url: string; attribution: string; service_area: number[]; service_center: number[]; service_radius_km: number };

let cachedConfig: MapConfiguration | null = null;

const uniquePlaces = (places: LocationOption[]): LocationOption[] => {
  const seen = new Set<string>();
  return places.filter(place => {
    const identity = place.place_id
      ?? `${place.latitude.toFixed(6)}:${place.longitude.toFixed(6)}:${place.formatted_address.trim().toLowerCase()}`;
    if (seen.has(identity)) return false;
    seen.add(identity);
    return true;
  });
};

export const mapService = {
  async configuration(): Promise<MapConfiguration> {
    if (!cachedConfig) cachedConfig = (await apiClient.get<MapConfiguration>('/api/v1/maps/config')).data;
    return cachedConfig;
  },
  async search(query: string, scope: 'local' | 'outstation' = 'local'): Promise<LocationOption[]> {
    const places = (await apiClient.get<LocationOption[]>('/api/v1/maps/places', { params: { q: query, scope } })).data;
    return uniquePlaces(places);
  },
  async reverse(latitude: number, longitude: number, scope: 'local' | 'outstation' = 'local'): Promise<LocationOption> {
    return (await apiClient.get<LocationOption>('/api/v1/maps/reverse', { params: { latitude, longitude, scope } })).data;
  },
};
