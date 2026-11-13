import AsyncStorage from '@react-native-async-storage/async-storage';
import auth, { FirebaseAuthTypes } from '@react-native-firebase/auth';

import { apiClient } from '../../../services/apiClient';

const SESSION_KEY = '@cabapp/passenger-session';
const PROFILE_NAME_KEY = '@cabapp/passenger-profile-name';

// Firebase fictional phone numbers do not need Play Integrity/reCAPTCHA.
// Keep the bypass strictly inside Metro development builds; release builds
// always use Firebase's normal Android app verification.
if (__DEV__) {
  auth().settings.appVerificationDisabledForTesting = true;
}

export type AuthSession = { access_token: string; refresh_token: string; token_type: 'bearer' };
export type PhoneAuthIntent = 'login' | 'signup';
export type OtpRequestResult = {
  isDevOtp: boolean;
  phoneNumber: string;
  developmentOtp?: string | null;
  firebaseConfirmation?: FirebaseAuthTypes.ConfirmationResult;
};

const FIREBASE_TIMEOUT_MS = 30_000;

function withFirebaseTimeout<T>(operation: Promise<T>, code: string, message: string): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(
      () => reject(Object.assign(new Error(message), { code })),
      FIREBASE_TIMEOUT_MS,
    );
    operation.then(
      value => { clearTimeout(timer); resolve(value); },
      error => { clearTimeout(timer); reject(error); },
    );
  });
}

function cleanDigits(phone: string): string {
  const digits = phone.replace(/\D/g, '');
  if (digits.length === 12 && digits.startsWith('91')) {
    return digits.slice(2);
  }
  return digits;
}

export const authService = {
  async loginWithPassword(phoneNumber: string, pinOrPassword: string): Promise<AuthSession> {
    const canonicalPhone = cleanDigits(phoneNumber);
    const response = await apiClient.post<AuthSession>(
      '/api/v1/auth/passengers/login',
      { phone_number: canonicalPhone, password: pinOrPassword },
    );
    await AsyncStorage.setItem(SESSION_KEY, JSON.stringify(response.data));
    return response.data;
  },

  async requestOtp(phoneNumber: string, intent: PhoneAuthIntent): Promise<OtpRequestResult> {
    const canonicalPhone = cleanDigits(phoneNumber);

    if (intent === 'login') {
      // Preflight verifies that an active, verified account exists before sending OTP
      await apiClient.post('/api/v1/auth/passengers/firebase/login/preflight', {
        phone_number: canonicalPhone,
      });
    }

    if (auth().currentUser) {
      await withFirebaseTimeout(
        auth().signOut(),
        'auth/session-reset-timeout',
        'Previous phone session could not be reset.',
      );
    }

    try {
      const firebaseConfirmation = await withFirebaseTimeout(
        auth().signInWithPhoneNumber(`+91${canonicalPhone}`),
        'auth/otp-request-timeout',
        'OTP request timed out.',
      );
      return {
        isDevOtp: false,
        phoneNumber: canonicalPhone,
        firebaseConfirmation,
      };
    } catch (fbError: unknown) {
      // If Firebase fails in development mode, fallback to backend dev OTP
      if (__DEV__) {
        try {
          const response = await apiClient.post<{ message: string; development_otp?: string }>(
            '/api/v1/auth/passengers/otp/request',
            { phone_number: canonicalPhone },
          );
          return {
            isDevOtp: true,
            phoneNumber: canonicalPhone,
            developmentOtp: response.data.development_otp,
          };
        } catch {
          // Keep original Firebase error
        }
      }
      throw fbError;
    }
  },

  async verifyOtp(
    confirmation: OtpRequestResult,
    otp: string,
    intent: PhoneAuthIntent,
    fullName?: string,
    password?: string,
  ): Promise<AuthSession> {
    // Development OTP verification path
    if (confirmation.isDevOtp) {
      const response = await apiClient.post<AuthSession>(
        '/api/v1/auth/passengers/otp/verify',
        { phone_number: confirmation.phoneNumber, otp },
      );
      if (fullName && intent === 'signup') {
        try {
          await apiClient.patch(
            '/api/v1/passengers/me/profile',
            { full_name: fullName },
            { headers: { Authorization: `Bearer ${response.data.access_token}` } },
          );
        } catch {
          // Non-critical profile name update
        }
      }
      await AsyncStorage.setItem(SESSION_KEY, JSON.stringify(response.data));
      return response.data;
    }

    // Production Firebase verification path
    if (!confirmation.firebaseConfirmation) {
      throw new Error('Missing Firebase confirmation session.');
    }
    const firebaseUser = await withFirebaseTimeout(
      confirmation.firebaseConfirmation.confirm(otp),
      'auth/otp-verification-timeout',
      'OTP verification timed out.',
    );
    if (!firebaseUser || !firebaseUser.user) {
      throw new Error('Firebase did not return an authenticated user.');
    }
    const idToken = await withFirebaseTimeout(
      firebaseUser.user.getIdToken(true),
      'auth/token-timeout',
      'Secure sign-in token timed out.',
    );
    try {
      const route =
        intent === 'signup'
          ? '/api/v1/auth/passengers/firebase/signup'
          : '/api/v1/auth/passengers/firebase/login';
      const response = await apiClient.post<AuthSession>(route, {
        id_token: idToken,
        full_name: fullName,
        password: password,
      });
      await AsyncStorage.setItem(SESSION_KEY, JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      await auth().signOut();
      throw error;
    }
  },

  async clearSession(): Promise<void> {
    await AsyncStorage.removeItem(SESSION_KEY);
    if (auth().currentUser) await auth().signOut();
  },

  async hasSession(): Promise<boolean> {
    const value = await AsyncStorage.getItem(SESSION_KEY);
    if (!value) return false;
    try {
      return Boolean((JSON.parse(value) as AuthSession).access_token);
    } catch {
      await AsyncStorage.removeItem(SESSION_KEY);
      return false;
    }
  },

  async saveProfileName(name: string): Promise<void> {
    await AsyncStorage.setItem(PROFILE_NAME_KEY, name.trim());
  },

  async getProfileName(): Promise<string | null> {
    return AsyncStorage.getItem(PROFILE_NAME_KEY);
  },
};
