import { useState } from 'react';
import { Alert, Pressable, StyleSheet, View } from 'react-native';

import { DriverButton } from '../../../components/DriverButton';
import { DriverText } from '../../../components/DriverText';
import { DriverTextField } from '../../../components/DriverTextField';
import { colors, spacing } from '../../../theme';
import {
  driverAuthService,
  type DriverAuthIntent,
  type DriverOtpRequestResult,
  type DriverRegistrationIdentity,
  type DriverSession,
} from '../services/driverAuthService';
import { driverAuthError } from '../utils/driverAuthError';

type DriverPhoneAuthFormProps = {
  intent: DriverAuthIntent;
  onAuthenticated?: (session: DriverSession) => void;
  onPhoneVerified?: (identity: DriverRegistrationIdentity) => void;
};

export function DriverPhoneAuthForm({ intent, onAuthenticated, onPhoneVerified }: DriverPhoneAuthFormProps) {
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [confirmation, setConfirmation] = useState<DriverOtpRequestResult | null>(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const otpRequested = confirmation !== null;

  const validate = (requireOtp: boolean) => {
    if (intent === 'signup' && fullName.trim().length < 2) return 'Enter your full name.';
    if (!/^[6-9]\d{9}$/.test(phone)) return 'Enter a valid 10-digit Indian mobile number.';
    if (requireOtp && !/^\d{6}$/.test(otp)) return 'Enter the six-digit OTP.';
    return null;
  };

  const requestOtp = async (restartChallenge = false) => {
    const validationError = validate(false);
    if (validationError) {
      setMessage(validationError);
      return;
    }
    setLoading(true);
    setMessage('');
    try {
      setOtp('');
      setConfirmation(null);
      if (restartChallenge) await driverAuthService.resetPhoneChallenge();
      const result = await driverAuthService.requestOtp(phone, intent);
      setConfirmation(result);
      if (result.isDevOtp && result.developmentOtp) {
        setOtp(result.developmentOtp);
        Alert.alert(
          'Development OTP',
          `Your test OTP is: ${result.developmentOtp}\n\n(Auto-filled for convenience)`,
        );
      } else {
        Alert.alert(
          'OTP sent',
          `Check the SMS inbox for +91${phone}. Firebase test numbers use the OTP configured in Firebase Console.`,
        );
      }
    } catch (error) {
      setMessage(driverAuthError(error));
    } finally {
      setLoading(false);
    }
  };

  const verify = async () => {
    const validationError = validate(true);
    if (validationError) {
      setMessage(validationError);
      return;
    }
    if (!confirmation) return;
    setLoading(true);
    setMessage('');
    try {
      if (intent === 'signup') {
        const identity = await driverAuthService.verifySignupPhone(confirmation, otp, fullName);
        onPhoneVerified?.(identity);
      } else {
        const session = await driverAuthService.verifyOtp(confirmation, otp, 'login');
        onAuthenticated?.(session);
      }
    } catch (error) {
      setMessage(driverAuthError(error));
    } finally {
      setLoading(false);
    }
  };

  const changePhone = async () => {
    if (loading) return;
    setLoading(true);
    setConfirmation(null);
    setOtp('');
    setPhone('');
    setMessage('');
    try {
      await driverAuthService.resetPhoneChallenge();
    } catch (error) {
      setMessage(driverAuthError(error));
    } finally {
      setLoading(false);
    }
  };

  const editPhone = (value: string) => {
    setPhone(value.replace(/\D/g, ''));
    setConfirmation(null);
    setOtp('');
    setMessage('');
  };

  return (
    <View style={styles.form}>
      {intent === 'signup' ? (
        <DriverTextField
          label="Full Name"
          onChangeText={value => {
            setFullName(value);
            setMessage('');
          }}
          placeholder="Enter your full name"
          value={fullName}
        />
      ) : null}
      <DriverTextField
        inputMode="numeric"
        label="Phone Number"
        leading={<DriverText color={colors.textSecondary} weight="600">+91</DriverText>}
        maxLength={10}
        onChangeText={editPhone}
        placeholder="98765 43210"
        value={phone}
      />
      {otpRequested ? (
        <>
          <DriverTextField
            inputMode="numeric"
            label="OTP"
            maxLength={6}
            onChangeText={value => {
              setOtp(value.replace(/\D/g, ''));
              setMessage('');
            }}
            placeholder="Enter six-digit OTP"
            value={otp}
          />
          <View style={styles.otpActions}>
            <Pressable accessibilityRole="button" disabled={loading} onPress={() => void changePhone()}>
              <DriverText color={loading ? colors.textTertiary : colors.primary} weight="600">
                Change number
              </DriverText>
            </Pressable>
            <Pressable accessibilityRole="button" disabled={loading} onPress={() => void requestOtp(true)}>
              <DriverText color={loading ? colors.textTertiary : colors.primary} weight="600">
                Resend OTP
              </DriverText>
            </Pressable>
          </View>
        </>
      ) : null}
      {message ? <DriverText color={colors.error}>{message}</DriverText> : null}
      <DriverButton
        label={otpRequested ? (intent === 'login' ? 'Verify & Login' : 'Verify & Continue') : 'Send OTP'}
        loading={loading}
        onPress={() => void (otpRequested ? verify() : requestOtp())}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  form: { gap: spacing.lg },
  otpActions: { flexDirection: 'row', justifyContent: 'space-between' },
});
