import { KeyboardAvoidingView, Platform, Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';

import { DriverAuthHeader } from '../../../components/auth/DriverAuthHeader';
import { DriverText } from '../../../components/DriverText';
import { colors, spacing } from '../../../theme';
import { DriverPhoneAuthForm } from '../components/DriverPhoneAuthForm';
import type { DriverSession } from '../services/driverAuthService';

type Props = { onAuthenticated: (session: DriverSession) => void; onBack: () => void; onHelp: () => void; onSignup: () => void };

export function DriverLoginScreen({ onAuthenticated, onBack, onHelp, onSignup }: Props) {
  return <SafeAreaView style={styles.safe}><KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.flex}><DriverAuthHeader onBack={onBack} onHelp={onHelp}/><ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled"><View style={styles.form}><DriverText color={colors.primary} size={30} style={styles.title} weight="700">Welcome{'\n'}Login Now!</DriverText><DriverText color={colors.textSecondary} style={styles.intro}>Sign in with your verified Driver mobile number.</DriverText><DriverPhoneAuthForm intent="login" onAuthenticated={onAuthenticated}/><View style={styles.switch}><DriverText color={colors.textSecondary}>Don’t have a Driver account?</DriverText><Pressable accessibilityRole="button" onPress={onSignup}><DriverText color={colors.primary} weight="600">Sign Up</DriverText></Pressable></View></View></ScrollView></KeyboardAvoidingView></SafeAreaView>;
}

const styles = StyleSheet.create({ safe: { backgroundColor: colors.surface, flex: 1 }, flex: { flex: 1 }, content: { flexGrow: 1, padding: spacing.xl, paddingTop: 72 }, form: { alignSelf: 'center', gap: spacing.xl, maxWidth: 520, width: '100%' }, title: { textAlign: 'center' }, intro: { textAlign: 'center' }, switch: { alignItems: 'center', flexDirection: 'row', gap: 4, justifyContent: 'center', marginTop: spacing.xl } });
