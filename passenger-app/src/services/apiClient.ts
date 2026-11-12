import axios, { AxiosError, AxiosHeaders, type InternalAxiosRequestConfig } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { environment } from '../config/environment';

export const PASSENGER_SESSION_KEY = '@cabapp/passenger-session';

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

type StoredSession = {
  access_token: string;
  refresh_token: string;
  [key: string]: unknown;
};

type RetryConfig = InternalAxiosRequestConfig & {
  _retriedAfterRefresh?: boolean;
};

let refreshPromise: Promise<string | null> | null = null;

const refreshAccessToken = async (): Promise<string | null> => {
  if (refreshPromise) return refreshPromise;
  refreshPromise = (async () => {
    const saved = await AsyncStorage.getItem(PASSENGER_SESSION_KEY);
    if (!saved) return null;
    try {
      const session = JSON.parse(saved) as StoredSession;
      if (!session.refresh_token) return null;
      const response = await axios.post<StoredSession>(
        `${environment.apiBaseUrl}/api/v1/auth/passengers/refresh`,
        { refresh_token: session.refresh_token },
        { timeout: environment.apiTimeoutMs },
      );
      const updated = { ...session, ...response.data };
      await AsyncStorage.setItem(PASSENGER_SESSION_KEY, JSON.stringify(updated));
      return updated.access_token;
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && (error.response?.status === 401 || error.response?.status === 403)) {
        // Only clear stored session when the server explicitly rejects the refresh token
        await AsyncStorage.removeItem(PASSENGER_SESSION_KEY);
      }
      return null;
    }
  })().finally(() => {
    refreshPromise = null;
  });
  return refreshPromise;
};

const createRequestId = (): string =>
  `passenger-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;

const toApiError = (error: unknown): ApiError => {
  if (!axios.isAxiosError(error)) {
    return new ApiError('An unexpected connection error occurred.');
  }

  const axiosError = error as AxiosError<{ detail?: string; message?: string }>;
  if (axiosError.code === 'ECONNABORTED') {
    return new ApiError('The request timed out. Please try again.');
  }

  if (!axiosError.response) {
    return new ApiError('Unable to reach the backend. Check your connection and try again.');
  }

  return new ApiError(
    axiosError.response.data?.detail ??
      axiosError.response.data?.message ??
      'The backend returned an unexpected error.',
    axiosError.response.status,
  );
};

export const apiClient = axios.create({
  baseURL: environment.apiBaseUrl,
  timeout: environment.apiTimeoutMs,
});

apiClient.interceptors.request.use(async (config) => {
  const headers = AxiosHeaders.from(config.headers);
  const savedSession = await AsyncStorage.getItem(PASSENGER_SESSION_KEY);
  let accessToken: string | undefined;
  try {
    accessToken = savedSession
      ? (JSON.parse(savedSession).access_token as string | undefined)
      : undefined;
  } catch {
    await AsyncStorage.removeItem(PASSENGER_SESSION_KEY);
  }
  headers.set('Accept', 'application/json');
  headers.set('X-Request-ID', createRequestId());
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`);
  config.headers = headers;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401 && error.config) {
      const config = error.config as RetryConfig;
      if (!config._retriedAfterRefresh && !config.url?.includes('/auth/passengers/refresh')) {
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

    const apiError = toApiError(error);
    if (
      axios.isAxiosError(error) &&
      error.response?.status === 401 &&
      (error.config?.url?.includes('/auth/passengers/refresh') || (error.config as RetryConfig)?._retriedAfterRefresh)
    ) {
      // Only clear credentials if the refresh request itself was rejected by the server
      await AsyncStorage.removeItem(PASSENGER_SESSION_KEY);
    }
    return Promise.reject(apiError);
  },
);
