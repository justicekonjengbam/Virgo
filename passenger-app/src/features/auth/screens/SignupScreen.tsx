import { useState } from 'react';
import { Alert, KeyboardAvoidingView, Platform, Pressable, SafeAreaView, ScrollView, StyleSheet, View, useWindowDimensions } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { AuthHeader } from '../../../components/auth/AuthHeader';
import { AuthInput } from '../../../components/auth/AuthInput';
import { AuthPrompt } from '../../../components/auth/AuthPrompt';
import { DsButton, DsText } from '../../../components/design-system';
import { colors, spacing } from '../../../theme';
import { authService, OtpRequestResult } from '../services/authService';
import { authErrorMessage } from '../utils/authErrorMessage';
import { validateFullName, validateIndianMobile, validateOtp, validatePin } from '../validation/authValidation';

type SignupScreenProps = { onAuthenticated: () => void; onBack: () => void; onHelp: () => void; onLogin: () => void };

/** Phone-first account creation screen; Firebase verifies ownership before the user enters the app. */
export function SignupScreen({ onAuthenticated, onBack, onHelp, onLogin }: SignupScreenProps) {
  const { width } = useWindowDimensions();
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [pin, setPin] = useState('');
  const [otp, setOtp] = useState('');
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [confirmation, setConfirmation] = useState<OtpRequestResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [fullNameError, setFullNameError] = useState<string | undefined>();
  const [phoneError, setPhoneError] = useState<string | undefined>();
  const [pinError, setPinError] = useState<string | undefined>();
  const [otpError, setOtpError] = useState<string | undefined>();
  const pagePadding = Math.max(spacing.xl, Math.min(42, width * 0.055));
  const otpRequested = confirmation !== null;

  const submit = async () => {
    const nextNameError = validateFullName(fullName);
    const nextPhoneError = validateIndianMobile(phone);
    const nextPinError = validatePin(pin);
    const nextOtpError = otpRequested ? validateOtp(otp) : undefined;
    setFullNameError(nextNameError);
    setPhoneError(nextPhoneError);
    setPinError(nextPinError);
    setOtpError(nextOtpError);
    if (nextNameError || nextPhoneError || nextPinError || nextOtpError) {
      setErrorMessage('Please correct the highlighted fields.');
      return;
    }
    if (!termsAccepted) {
      setErrorMessage('Accept the Terms & Conditions and Privacy Policy to continue.');
      return;
    }
    setSubmitting(true);
    setErrorMessage('');
    try {
      if (!confirmation) {
        const result = await authService.requestOtp(phone, 'signup');
        setConfirmation(result);
        if (result.isDevOtp && result.developmentOtp) {
          setOtp(result.developmentOtp);
          Alert.alert(
            'Development OTP',
            `Your test OTP is: ${result.developmentOtp}\n\n(Auto-filled for convenience in development mode)`,
          );
        } else {
          Alert.alert('OTP requested', 'For a real number, check its SMS inbox. For a Firebase test number, use the test OTP configured in Firebase Console.');
        }
      } else {
        await authService.verifyOtp(confirmation, otp, 'signup', fullName, pin);
        await authService.saveProfileName(fullName);
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
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.flex}>
        <AuthHeader onBack={onBack} onHelp={onHelp} />
        <ScrollView contentContainerStyle={[styles.scrollContent, { paddingHorizontal: pagePadding }]} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>
          <View style={styles.form}>
            <DsText color={colors.primary} variant="display" style={styles.title}>Create an Account</DsText>
            <DsText color={colors.textSecondary} style={styles.intro}>Create your account with a verified mobile number.</DsText>
            <View style={styles.fields}>
              <AuthInput
                error={fullNameError}
                icon="account"
                label="Full Name"
                onChangeText={value => { setFullName(value); setFullNameError(undefined); setErrorMessage(''); }}
                placeholder="Enter your full name"
                value={fullName}
              />
              <AuthInput
                error={phoneError}
                icon="phone"
                inputMode="numeric"
                label="Phone Number"
                maxLength={10}
                onChangeText={value => {
                  setPhone(value.replace(/\D/g, ''));
                  setOtp('');
                  setConfirmation(null);
                  setPhoneError(undefined);
                  setErrorMessage('');
                }}
                placeholder="98765 43210"
                prefix="+91"
                value={phone}
              />
              <AuthInput
                error={pinError}
                icon="shield-key"
                inputMode="numeric"
                label="Security PIN (4 digits)"
                maxLength={4}
                onChangeText={value => {
                  setPin(value.replace(/\D/g, ''));
                  setPinError(undefined);
                  setErrorMessage('');
                }}
                placeholder="Choose a 4-digit PIN for instant login"
                secureTextEntry
                value={pin}
              />
              {otpRequested ? (
                <AuthInput
                  error={otpError}
                  icon="lock"
                  inputMode="numeric"
                  label="OTP Verification"
                  maxLength={6}
                  onChangeText={value => {
                    setOtp(value.replace(/\D/g, ''));
                    setOtpError(undefined);
                    setErrorMessage('');
                  }}
                  placeholder="Enter six-digit OTP"
                  value={otp}
                />
              ) : null}
            </View>
            <Pressable accessibilityRole="checkbox" accessibilityState={{ checked: termsAccepted }} onPress={() => setTermsAccepted(!termsAccepted)} style={styles.terms}>
              <MaterialCommunityIcons color={termsAccepted ? colors.primary : colors.textTertiary} name={termsAccepted ? 'checkbox-marked' : 'checkbox-blank-outline'} size={25} />
              <DsText color={colors.textSecondary} style={styles.termsText}>I agree to the <DsText color={colors.primary}>Terms & Conditions</DsText> and <DsText color={colors.primary}>Privacy Policy</DsText></DsText>
            </Pressable>
            {errorMessage ? <DsText color={colors.error}>{errorMessage}</DsText> : null}
            <DsButton label={otpRequested ? 'Verify & Create Account' : 'Send OTP'} loading={submitting} onPress={submit} size="large" />
            <AuthPrompt actionLabel="Login" message="Already have an account?" onAction={onLogin} />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  fields: { gap: spacing.lg }, flex: { flex: 1 }, form: { alignSelf: 'center', gap: spacing.xl, maxWidth: 560, paddingTop: spacing.xxxl, width: '100%' },
  intro: { textAlign: 'center' }, safeArea: { backgroundColor: colors.surface, flex: 1 }, scrollContent: { flexGrow: 1, paddingBottom: spacing.massive },
  terms: { alignItems: 'flex-start', flexDirection: 'row', gap: spacing.sm }, termsText: { flex: 1 }, title: { textAlign: 'center' },
});
