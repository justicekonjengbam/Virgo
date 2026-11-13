import axios from 'axios';

function readableDetail(value: unknown): string | null {
  if (typeof value === 'string' && value.trim()) return value;
  if (Array.isArray(value)) {
    const messages = value.map(readableDetail).filter((message): message is string => Boolean(message));
    return messages.length ? messages.join(' ') : null;
  }
  if (typeof value === 'object' && value !== null) {
    const record = value as Record<string, unknown>;
    if (typeof record.msg === 'string') return record.msg;
    if ('detail' in record) return readableDetail(record.detail);
    if (typeof record.message === 'string') return record.message;
  }
  return null;
}

/** Converts Firebase, Axios, and FastAPI/Pydantic errors into text safe for React Native. */
export function driverAuthError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = readableDetail(error.response?.data?.detail ?? error.response?.data);
    if (detail) return detail;
    if (error.code === 'ECONNABORTED') return 'Virgo took too long to respond. Check that the backend is running, then try again.';
    if (!error.response) return 'Unable to reach Virgo. Check that the backend is running and your device is connected, then try again.';
    if (error.response.status === 401) return 'Your sign-in session is no longer valid. Request a new OTP and try again.';
    if (error.response.status === 403) return 'Your Driver account is not active or not authorized.';
    if (error.response.status === 404) return 'No Driver account exists for this number. Please sign up first.';
    if (error.response.status === 409) return 'This information is already registered. Please review it and try again.';
    if (error.response.status >= 500) return 'Virgo is temporarily unavailable. Please try again in a moment.';
    return 'We could not complete that request. Please try again.';
  }
  const code = typeof error === 'object' && error !== null && 'code' in error ? String(error.code) : '';
  if (code === 'auth/invalid-phone-number') return 'Enter a valid Indian mobile number.';
  if (code === 'auth/invalid-verification-code') return 'The OTP is incorrect. Try again.';
  if (code === 'auth/session-expired') return 'The OTP has expired. Request a new one.';
  if (code === 'auth/too-many-requests') return 'Too many OTP attempts. Please wait and try again.';
  if (code === 'auth/otp-request-timeout') return 'OTP request timed out. Check the emulator network, then try again.';
  if (code === 'auth/otp-verification-timeout') return 'OTP verification timed out. Change the number, then request a fresh OTP.';
  if (code === 'auth/token-timeout') return 'Secure sign-in took too long. Please request a fresh OTP and try again.';
  if (code === 'auth/session-reset-timeout') return 'The previous phone session could not be reset. Close and reopen the app, then try again.';
  if (code === 'auth/app-not-authorized') return 'Firebase cannot verify this Driver app. Check its Android package and SHA fingerprints.';
  if (code.includes('billing') || code.includes('17499')) {
    return 'Firebase SMS billing is not enabled. Please use development mode.';
  }
  if (error instanceof Error && error.message.trim()) {
    const msg = error.message.trim();
    if (msg.includes('BILLING_NOT_ENABLED') || msg.includes('17499')) {
      return 'Firebase SMS billing is not enabled. Please use development mode.';
    }
    return msg;
  }
  return 'Something went wrong. Please try again.';
}
