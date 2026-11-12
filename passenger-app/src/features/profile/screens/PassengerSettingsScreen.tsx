import { useEffect, useState } from 'react';
import { SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';

import { AppPageHeader } from '../../../components/navigation/AppPageHeader';
import { DsButton, DsCard, DsEmptyState, DsLoading, DsText, DsTextField } from '../../../components/design-system';
import { colors, spacing } from '../../../theme';
import { passengerProfileApi, type PassengerProfile } from '../data/passengerProfileApi';

export function PassengerSettingsScreen({ onBack, onMenuPress }: { onBack: () => void; onMenuPress: () => void }) {
  const [profile, setProfile] = useState<PassengerProfile | null>(null); const [name, setName] = useState(''); const [email, setEmail] = useState(''); const [language, setLanguage] = useState('en'); const [saving, setSaving] = useState(false); const [message, setMessage] = useState('');
  useEffect(() => { void passengerProfileApi.get().then(value => { setProfile(value); setName(value.full_name); setEmail(value.email ?? ''); setLanguage(value.preferred_language); }).catch(() => setMessage('Unable to load your profile.')); }, []);
  const save = async () => { if (name.trim().length < 2) return setMessage('Enter a valid name.'); if (email && !/^\S+@\S+\.\S+$/.test(email)) return setMessage('Enter a valid email address.'); setSaving(true); setMessage(''); try { const updated = await passengerProfileApi.update({ full_name: name.trim(), email: email.trim() || null, preferred_language: language.trim() || 'en' }); setProfile(updated); setMessage('Profile saved successfully.'); } catch { setMessage('We could not save your profile. Check the details and try again.'); } finally { setSaving(false); } };
  if (!profile && !message) return <SafeAreaView style={styles.safe}><DsLoading fullScreen label="Loading profile…"/></SafeAreaView>;
  if (!profile) return <SafeAreaView style={styles.safe}><DsEmptyState actionLabel="Back" onAction={onBack} title={message}/></SafeAreaView>;
  return <SafeAreaView style={styles.safe}><ScrollView contentContainerStyle={styles.content}><AppPageHeader onBack={onBack} onMenuPress={onMenuPress} title="Settings"/><DsCard elevated style={styles.identity}><DsText variant="h2">Profile</DsText><DsText color={colors.textSecondary}>Manage the contact details used for Virgo updates.</DsText><DsTextField label="Full name" onChangeText={setName} value={name}/><DsTextField autoCapitalize="none" keyboardType="email-address" label="Email address" onChangeText={setEmail} placeholder="you@example.com" value={email}/><DsTextField editable={false} label="Verified phone number" value={profile.phone_number.replace(/\D/g,'').slice(-10)}/><DsTextField autoCapitalize="none" label="Preferred language" onChangeText={setLanguage} value={language}/>{message ? <DsText color={message.includes('success') ? colors.success : colors.error}>{message}</DsText> : null}<DsButton label="Save changes" loading={saving} onPress={() => void save()}/></DsCard><View style={styles.note}><DsText color={colors.textSecondary}>Phone number, authentication, saved addresses, and ride records cannot be edited here.</DsText></View></ScrollView></SafeAreaView>;
}
const styles = StyleSheet.create({ safe: { backgroundColor: colors.background, flex: 1 }, content: { gap: spacing.lg, padding: spacing.xl, paddingBottom: spacing.massive }, identity: { gap: spacing.md }, note: { paddingHorizontal: spacing.sm } });
