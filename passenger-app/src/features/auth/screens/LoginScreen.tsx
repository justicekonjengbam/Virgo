import { useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  View,
  useWindowDimensions,
} from 'react-native';

import { AuthHeader } from '../../../components/auth/AuthHeader';
import { AuthInput } from '../../../components/auth/AuthInput';
import { AuthPrompt } from '../../../components/auth/AuthPrompt';
import { RememberMe } from '../../../components/auth/RememberMe';
import { DsButton, DsText } from '../../../components/design-system';
import { colors, spacing } from '../../../theme';
import { authService, OtpRequestResult } from '../services/authService';
import { authErrorMessage } from '../utils/authErrorMessage';
import { validateIndianMobile, validateOtp } from '../validation/authValidation';

type LoginScreenProps = {
  onBack: () => void;
  onAuthenticated: () => void;
  onHelp: () => void;
  onSignup: () => void;
};

/** Responsive visual implementation of the Passenger login Figma frame. */
export function LoginScreen({ onBack, onAuthenticated, onHelp, onSignup }: LoginScreenProps) {
  const { width } = useWindowDimensions();
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [otpRequested, setOtpRequested] = useState(false);
  const [confirmation, setConfirmation] = useState<OtpRequestResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [phoneError, setPhoneError] = useState<string | undefined>();
  const [otpError, setOtpError] = useState<string | undefined>();
  const pagePadding = Math.max(spacing.xl, Math.min(42, width * 0.055));

  const submit = async () => {
    const nextPhoneError = validateIndianMobile(phone);
    const nextOtpError = otpRequested ? validateOtp(otp) : undefined;
    setPhoneError(nextPhoneError); setOtpError(nextOtpError);
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
            `Your test OTP is: ${result.developmentOtp}\n\n(Auto-filled for convenience)`,
          );
        } else {
          Alert.alert(
            'OTP requested',
            'For a real number, check its SMS inbox. For a Firebase test number, no SMS is sent—enter the test OTP configured in Firebase Console.',
          );
        }
      } else if (confirmation) {
        await authService.verifyOtp(confirmation, otp, 'login');
        onAuthenticated();
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
                placeholder="----- -----"
                prefix="+91"
                value={phone}
              />
              {otpRequested ? (
                <AuthInput
                  icon="lock"
                  inputMode="numeric"
                  error={otpError}
                  label="OTP"
                  maxLength={6}
                  onChangeText={(value) => { setOtp(value.replace(/\D/g, '')); setOtpError(undefined); setErrorMessage(''); }}
                  placeholder="Enter six-digit OTP"
                  value={otp}
                />
              ) : null}
            </View>
            <RememberMe checked={rememberMe} onChange={setRememberMe} />
            {errorMessage ? <DsText color={colors.error}>{errorMessage}</DsText> : null}
            <DsButton
              label={otpRequested ? 'Verify & Sign In' : 'Send OTP'}
              loading={submitting}
              onPress={submit}
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
  form: { alignSelf: 'center', gap: spacing.xxl, maxWidth: 560, paddingTop: 72, width: '100%' },
  title: { alignSelf: 'center', fontSize: 30, lineHeight: 38, textAlign: 'center' },
  fields: { gap: spacing.lg, marginTop: spacing.huge },
});
