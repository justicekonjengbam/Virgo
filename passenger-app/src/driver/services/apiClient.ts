import AsyncStorage from '@react-native-async-storage/async-storage';
import axios, { AxiosHeaders, type InternalAxiosRequestConfig } from 'axios';

import { environment } from '../config/environment';

export const DRIVER_SESSION_KEY = '@virgo/driver-session';
type StoredSession = { access_token: string; refresh_token: string; [key: string]: unknown };
type RetryConfig = InternalAxiosRequestConfig & { _retriedAfterRefresh?: boolean };
let refreshPromise: Promise<string | null> | null = null;

const refreshAccessToken = async (): Promise<string | null> => {
  if (refreshPromise) return refreshPromise;
  refreshPromise = (async () => {
    const saved = await AsyncStorage.getItem(DRIVER_SESSION_KEY);
    if (!saved) return null;
    try {
      const session = JSON.parse(saved) as StoredSession;
      if (!session.refresh_token) return null;
      const response = await axios.post<StoredSession>(`${environment.apiBaseUrl}/api/v1/auth/drivers/refresh`, { refresh_token: session.refresh_token }, { timeout: environment.apiTimeoutMs });
      const updated = { ...session, ...response.data };
      await AsyncStorage.setItem(DRIVER_SESSION_KEY, JSON.stringify(updated));
      return updated.access_token;
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && (error.response?.status === 401 || error.response?.status === 403)) {
        await AsyncStorage.removeItem(DRIVER_SESSION_KEY);
      }
      return null;
    }
  })().finally(() => { refreshPromise = null; });
  return refreshPromise;
};

export const apiClient = axios.create({
  baseURL: environment.apiBaseUrl,
  timeout: environment.apiTimeoutMs,
});

apiClient.interceptors.request.use(async config => {
  const headers = AxiosHeaders.from(config.headers);
  const savedSession = await AsyncStorage.getItem(DRIVER_SESSION_KEY);
  try {
    const accessToken = savedSession ? (JSON.parse(savedSession) as { access_token?: string }).access_token : undefined;
    if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`);
  } catch {
    await AsyncStorage.removeItem(DRIVER_SESSION_KEY);
  }
  headers.set('Accept', 'application/json');
  headers.set('X-Request-ID', `driver-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`);
  config.headers = headers;
  return config;
});

apiClient.interceptors.response.use(
  response => response,
  async error => {
    if (axios.isAxiosError(error) && error.response?.status === 401 && error.config) {
      const config = error.config as RetryConfig;
      if (!config._retriedAfterRefresh && !config.url?.includes('/auth/drivers/refresh')) {
        config._retriedAfterRefresh = true;
        const token = await refreshAccessToken();
        if (token) {
          const headers = AxiosHeaders.from(config.headers);
          headers.set('Authorization', `Bearer ${token}`);
          config.headers = headers;
          return apiClient.request(config);
        }
      }
    }
    return Promise.reject(error);
  },
);
