import { ApiError } from '../../../services/apiClient';

/** Converts Firebase and API errors into clear, actionable auth feedback. */
export function authErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  const code = typeof error === 'object' && error && 'code' in error ? String(error.code) : '';
  if (code === 'auth/invalid-phone-number') return 'Enter a valid Indian mobile number.';
  if (code === 'auth/invalid-verification-code') return 'The OTP is incorrect. Try again.';
  if (code === 'auth/session-expired') return 'The OTP has expired. Request a new one.';
  if (code === 'auth/too-many-requests' || code === 'auth/quota-exceeded') return 'Too many OTP attempts. Please wait before trying again.';
  if (code === 'auth/network-request-failed') return 'Network error. Check your internet connection and try again.';
  if (code === 'auth/otp-request-timeout') return 'OTP request timed out. Check the emulator internet connection and try again.';
  if (code === 'auth/otp-verification-timeout') return 'OTP verification timed out. Use Change number, then request a fresh OTP.';
  if (code === 'auth/token-timeout') return 'Secure sign-in took too long. Please request a fresh OTP and try again.';
  if (code === 'auth/session-reset-timeout') return 'The previous phone session could not be reset. Close and reopen the app, then try again.';
  if (code === 'auth/operation-not-allowed') return 'Phone sign-in is disabled in Firebase. Enable it in Firebase Console.';
  if (code === 'auth/app-not-authorized') return 'Firebase cannot verify this Android app. Check its SHA-1 and SHA-256 fingerprints.';
  if (code === 'auth/captcha-check-failed') return 'Firebase app verification failed. Complete the verification and try again.';
  if (code === 'auth/missing-activity-for-recaptcha') return 'Firebase needs an Android activity to complete phone verification. Restart the app and try again.';
  return 'Unable to continue. Please try again.';
}
