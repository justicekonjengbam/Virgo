import { useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';

import { DriverAuthHeader } from '../../../components/auth/DriverAuthHeader';
import { DriverText } from '../../../components/DriverText';
import { colors, spacing } from '../../../theme';
import { DriverPhoneAuthForm } from '../components/DriverPhoneAuthForm';
import { DriverVehicleVerificationForm } from '../components/DriverVehicleVerificationForm';
import type { DriverRegistrationIdentity, DriverSession } from '../services/driverAuthService';

type Props = { onAuthenticated: (session: DriverSession) => void; onBack: () => void; onHelp: () => void; onLogin: () => void };

export function DriverSignupScreen({ onAuthenticated, onBack, onHelp, onLogin }: Props) {
  const [step, setStep] = useState<1 | 2>(1);
  const [identity, setIdentity] = useState<DriverRegistrationIdentity | null>(null);
  const onBasicDetailsVerified = (verifiedIdentity: DriverRegistrationIdentity) => { setIdentity(verifiedIdentity); setStep(2); };
  return <SafeAreaView style={styles.safe}><KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.flex}><DriverAuthHeader onBack={step === 1 ? onBack : () => setStep(1)} onHelp={onHelp} onLogin={onLogin}/><ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled"><View style={styles.form}><DriverText color={colors.primary} size={30} style={styles.title} weight="700">Create an Account</DriverText><StepIndicator activeStep={step}/>{step === 1 ? <><DriverText color={colors.textSecondary} style={styles.intro}>Verify your mobile number. Your Driver application is saved only after Step 2.</DriverText><DriverPhoneAuthForm intent="signup" onPhoneVerified={onBasicDetailsVerified}/></> : identity ? <DriverVehicleVerificationForm identity={identity} onCompleted={onAuthenticated}/> : null}<View style={styles.login}><DriverText color={colors.textSecondary}>Already have an account?</DriverText><Pressable accessibilityRole="button" onPress={onLogin}><DriverText color={colors.primary} weight="600">Login</DriverText></Pressable></View></View></ScrollView></KeyboardAvoidingView></SafeAreaView>;
}

function StepIndicator({ activeStep }: { activeStep: 1 | 2 }) {
  return <><View style={styles.steps}><View style={styles.stepActive}><DriverText color={colors.white} weight="600">1</DriverText></View><View style={styles.line}/><View style={activeStep === 2 ? styles.stepActive : styles.step}><DriverText color={activeStep === 2 ? colors.white : colors.textTertiary} weight="600">2</DriverText></View></View><View style={styles.labels}><DriverText color={activeStep === 1 ? colors.textPrimary : colors.textTertiary} weight="500">Basic Details</DriverText><DriverText color={activeStep === 2 ? colors.textPrimary : colors.textTertiary} weight={activeStep === 2 ? '500' : '400'}>Verify Documents</DriverText></View></>;
}

const styles = StyleSheet.create({ safe: { backgroundColor: colors.surface, flex: 1 }, flex: { flex: 1 }, content: { flexGrow: 1, padding: spacing.xl, paddingBottom: spacing.massive }, form: { alignSelf: 'center', gap: spacing.lg, maxWidth: 520, width: '100%' }, title: { textAlign: 'center' }, steps: { alignItems: 'center', flexDirection: 'row', paddingHorizontal: spacing.xxl }, step: { alignItems: 'center', borderColor: colors.borderStrong, borderRadius: 16, borderWidth: 1, height: 32, justifyContent: 'center', width: 32 }, stepActive: { alignItems: 'center', backgroundColor: colors.primary, borderRadius: 16, height: 32, justifyContent: 'center', width: 32 }, line: { backgroundColor: colors.primary, flex: 1, height: 1 }, labels: { flexDirection: 'row', justifyContent: 'space-between' }, intro: { textAlign: 'center' }, login: { alignItems: 'center', flexDirection: 'row', gap: 4, justifyContent: 'center', marginTop: spacing.lg } });
