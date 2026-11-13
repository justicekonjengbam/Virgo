import { useEffect, useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  View,
  useWindowDimensions,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { AuthHeader } from '../../../components/auth/AuthHeader';
import { AuthInput } from '../../../components/auth/AuthInput';
import { AuthPrompt } from '../../../components/auth/AuthPrompt';
import { RememberMe } from '../../../components/auth/RememberMe';
import { DsButton, DsText } from '../../../components/design-system';
import { colors, spacing } from '../../../theme';
import { authService, OtpRequestResult } from '../services/authService';
import { authErrorMessage } from '../utils/authErrorMessage';
import { validateIndianMobile, validateOtp, validatePin } from '../validation/authValidation';

const REMEMBERED_PHONE_KEY = '@cabapp/remembered-phone';

type LoginScreenProps = {
  onBack: () => void;
  onAuthenticated: () => void;
  onHelp: () => void;
  onSignup: () => void;
};

/**
 * Passenger login screen supporting cost-free 4-digit PIN authentication
 * with instant fallback to Firebase SMS OTP verification and PIN recovery.
 */
export function LoginScreen({ onBack, onAuthenticated, onHelp, onSignup }: LoginScreenProps) {
  const { width } = useWindowDimensions();
  const [authMode, setAuthMode] = useState<'pin' | 'otp'>('pin');
  const [phone, setPhone] = useState('');
  const [pin, setPin] = useState('');
  const [newPin, setNewPin] = useState('');
  const [otp, setOtp] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [otpRequested, setOtpRequested] = useState(false);
  const [confirmation, setConfirmation] = useState<OtpRequestResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [phoneError, setPhoneError] = useState<string | undefined>();
  const [pinError, setPinError] = useState<string | undefined>();
  const [otpError, setOtpError] = useState<string | undefined>();
  const pagePadding = Math.max(spacing.xl, Math.min(42, width * 0.055));

  // Load remembered phone on mount
  useEffect(() => {
    AsyncStorage.getItem(REMEMBERED_PHONE_KEY)
      .then((savedPhone) => {
        if (savedPhone) {
          setPhone(savedPhone);
          setRememberMe(true);
        }
      })
      .catch(() => {});
  }, []);

  const handleSuccessfulAuth = async () => {
    if (rememberMe && phone) {
      await AsyncStorage.setItem(REMEMBERED_PHONE_KEY, phone);
    } else {
      await AsyncStorage.removeItem(REMEMBERED_PHONE_KEY);
    }
    onAuthenticated();
  };

  const handlePinLogin = async () => {
    const nextPhoneError = validateIndianMobile(phone);
    const nextPinError = validatePin(pin);
    setPhoneError(nextPhoneError);
    setPinError(nextPinError);
    if (nextPhoneError || nextPinError) {
      setErrorMessage('Please enter a valid phone number and 4-digit PIN.');
      return;
    }

    setSubmitting(true);
    setErrorMessage('');
    try {
      await authService.loginWithPassword(phone, pin);
      await handleSuccessfulAuth();
    } catch (error) {
      setErrorMessage(authErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const handleOtpFlow = async () => {
    const nextPhoneError = validateIndianMobile(phone);
    const nextOtpError = otpRequested ? validateOtp(otp) : undefined;
    setPhoneError(nextPhoneError);
    setOtpError(nextOtpError);
    if (nextPhoneError || nextOtpError) {
      setErrorMessage('Please correct the highlighted fields.');
      return;
    }

    setSubmitting(true);
    setErrorMessage('');
    try {
      if (!otpRequested) {
        const result = await authService.requestOtp(phone, 'login');
        setConfirmation(result);
        setOtpRequested(true);
        if (result.isDevOtp && result.developmentOtp) {
          setOtp(result.developmentOtp);
          Alert.alert(
            'Development OTP',
            `Your test OTP is: ${result.developmentOtp}\n\n(Auto-filled for convenience in development mode)`,
          );
        } else {
          Alert.alert(
            'OTP Sent',
            'Check your SMS inbox for the verification code. Enter it below to sign in.',
          );
        }
      } else if (confirmation) {
        await authService.verifyOtp(confirmation, otp, 'login', undefined, newPin || undefined);
        await handleSuccessfulAuth();
      }
    } catch (error) {
      setErrorMessage(authErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.flex}
      >
        <AuthHeader onBack={onBack} onHelp={onHelp} />
        <ScrollView
          contentContainerStyle={[styles.scrollContent, { paddingHorizontal: pagePadding }]}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.form}>
            <DsText color={colors.primary} variant="display" style={styles.title}>
              Welcome{`\n`}Login Now!
            </DsText>

            <DsText color={colors.textSecondary} style={styles.intro}>
              {authMode === 'pin'
                ? 'Sign in instantly with your registered mobile and 4-digit PIN.'
                : 'Sign in using SMS OTP verification.'}
            </DsText>

            <View style={styles.fields}>
              <AuthInput
                icon="phone"
                inputMode="numeric"
                error={phoneError}
                label="Phone Number"
                maxLength={10}
                onChangeText={(value) => {
                  setPhone(value.replace(/\D/g, ''));
                  setOtp('');
                  setOtpRequested(false);
                  setConfirmation(null);
                  setPhoneError(undefined);
                  setErrorMessage('');
                }}
                placeholder="98765 43210"
                prefix="+91"
                value={phone}
              />

              {authMode === 'pin' ? (
                <AuthInput
                  error={pinError}
                  icon="shield-key"
                  inputMode="numeric"
                  label="Security PIN (4 digits)"
                  maxLength={4}
                  onChangeText={(value) => {
                    setPin(value.replace(/\D/g, ''));
                    setPinError(undefined);
                    setErrorMessage('');
                  }}
                  placeholder="Enter 4-digit PIN"
                  secureTextEntry
                  value={pin}
                />
              ) : null}

              {authMode === 'otp' && otpRequested ? (
                <>
                  <AuthInput
                    error={otpError}
                    icon="lock"
                    inputMode="numeric"
                    label="OTP Verification"
                    maxLength={6}
                    onChangeText={(value) => {
                      setOtp(value.replace(/\D/g, ''));
                      setOtpError(undefined);
                      setErrorMessage('');
                    }}
                    placeholder="Enter six-digit OTP"
                    value={otp}
                  />

                  <AuthInput
                    icon="shield-key"
                    inputMode="numeric"
                    label="Reset PIN (Optional)"
                    maxLength={4}
                    onChangeText={(value) => setNewPin(value.replace(/\D/g, ''))}
                    placeholder="Set new 4-digit PIN"
                    secureTextEntry
                    value={newPin}
                  />
                </>
              ) : null}
            </View>

            <View style={styles.optionsRow}>
              <RememberMe checked={rememberMe} onChange={setRememberMe} />

              <Pressable
                onPress={() => {
                  setErrorMessage('');
                  if (authMode === 'pin') {
                    setAuthMode('otp');
                    setOtpRequested(false);
                    setConfirmation(null);
                  } else {
                    setAuthMode('pin');
                    setOtpRequested(false);
                    setConfirmation(null);
                  }
                }}
              >
                <DsText color={colors.primary} variant="caption" style={styles.switchModeText}>
                  {authMode === 'pin' ? 'Forgot PIN? / Use OTP' : 'Use PIN Login instead'}
                </DsText>
              </Pressable>
            </View>

            {errorMessage ? <DsText color={colors.error}>{errorMessage}</DsText> : null}

            <DsButton
              label={
                authMode === 'pin'
                  ? 'Sign In'
                  : otpRequested
                  ? 'Verify & Sign In'
                  : 'Send OTP'
              }
              loading={submitting}
              onPress={authMode === 'pin' ? handlePinLogin : handleOtpFlow}
              size="large"
            />

            <AuthPrompt
              actionLabel="Sign Up"
              message="Don’t have an account?"
              onAction={onSignup}
            />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  safeArea: { backgroundColor: colors.surface, flex: 1 },
  scrollContent: { flexGrow: 1, paddingBottom: spacing.massive },
  form: { alignSelf: 'center', gap: spacing.xl, maxWidth: 560, paddingTop: 40, width: '100%' },
  title: { alignSelf: 'center', fontSize: 30, lineHeight: 38, textAlign: 'center' },
  intro: { textAlign: 'center', marginTop: -spacing.md },
  fields: { gap: spacing.lg, marginTop: spacing.md },
  optionsRow: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
  },
  switchModeText: {
    textDecorationLine: 'underline',
    fontWeight: '600',
  },
});
