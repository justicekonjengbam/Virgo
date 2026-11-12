import Config from 'react-native-config';

const DEFAULT_API_BASE_URL = 'http://10.0.2.2:8000';
const DEFAULT_API_TIMEOUT_MS = 10_000;

const parseTimeout = (value?: string): number => {
  const timeout = Number(value);
  return Number.isFinite(timeout) && timeout > 0 ? timeout : DEFAULT_API_TIMEOUT_MS;
};

const normalizeUrl = (url?: string): string =>
  (url ?? DEFAULT_API_BASE_URL).replace(/\/api\/v1\/?$/, '').replace(/\/$/, '');

export const environment = {
  apiBaseUrl: normalizeUrl(Config.API_BASE_URL),
  apiTimeoutMs: parseTimeout(Config.API_TIMEOUT_MS),
  wsBaseUrl: (Config.WS_BASE_URL ?? (Config.API_BASE_URL ?? DEFAULT_API_BASE_URL).replace(/^http/, 'ws')).replace(/\/$/, ''),
} as const;
