import { useEffect, useState } from 'react';
import { ActivityIndicator, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DriverButton } from '../../../components/DriverButton';
import { DriverCard } from '../../../components/DriverCard';
import { DriverPageHeader } from '../../../components/DriverPageHeader';
import { DriverText } from '../../../components/DriverText';
import { DriverTextField } from '../../../components/DriverTextField';
import { colors, spacing } from '../../../theme';
import { driverAuthError } from '../../auth/utils/driverAuthError';
import { driverProfileService, type DriverProfile } from '../services/driverProfileService';

export function DriverSettingsScreen({ onBack, onSwitchToPassenger }: { onBack: () => void; onSwitchToPassenger?: () => void }) {
  const [profile, setProfile] = useState<DriverProfile | null>(null);
  const [fullName, setFullName] = useState(''); const [city, setCity] = useState('');
  const [error, setError] = useState<string | null>(null); const [isSaving, setIsSaving] = useState(false); const [saved, setSaved] = useState(false);
  useEffect(() => {
    void driverProfileService.get().then(next => { setProfile(next); setFullName(next.full_name); setCity(next.operating_city ?? ''); }).catch(cause => setError(driverAuthError(cause)));
  }, []);
  async function save() {
    const name = fullName.trim(); const operatingCity = city.trim();
    if (name.length < 2) { setError('Enter your full name using at least 2 characters.'); return; }
    if (operatingCity.length < 2) { setError('Enter the city where you operate.'); return; }
    setIsSaving(true); setError(null); setSaved(false);
    try { const updated = await driverProfileService.update({ full_name: name, operating_city: operatingCity }); setProfile(updated); setFullName(updated.full_name); setCity(updated.operating_city ?? ''); setSaved(true); }
    catch (cause) { setError(driverAuthError(cause)); } finally { setIsSaving(false); }
  }
  return <SafeAreaView style={styles.safe}><DriverPageHeader onBack={onBack} title="Settings"/><ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled"><DriverText size={25} weight="700">Profile settings</DriverText><DriverText color={colors.textSecondary}>Keep your contact preferences and operating location up to date.</DriverText>{!profile && !error ? <View style={styles.loading}><ActivityIndicator color={colors.primary} size="large"/><DriverText color={colors.textSecondary}>Loading your profile…</DriverText></View> : <><DriverCard style={styles.card}><DriverText weight="700">Editable information</DriverText><DriverTextField label="Full name" onChangeText={value => { setFullName(value); setSaved(false); }} placeholder="Enter your full name" value={fullName}/><DriverTextField label="Place of operation" onChangeText={value => { setCity(value); setSaved(false); }} placeholder="e.g. Imphal" value={city}/><DriverButton label="Save changes" loading={isSaving} onPress={() => void save()}/>{error ? <DriverText color={colors.error}>{error}</DriverText> : null}{saved ? <DriverText color={colors.success} weight="600">Your profile changes are saved.</DriverText> : null}</DriverCard>{onSwitchToPassenger ? <DriverCard style={styles.modeCard}><View style={styles.readOnly}><View style={styles.modeIcon}><MaterialCommunityIcons color={colors.primary} name="car-clock" size={26}/></View><View style={styles.readOnlyCopy}><DriverText weight="700">Passenger Mode</DriverText><DriverText color={colors.textSecondary} size={13}>Switch to passenger mode to book rides for yourself across Imphal.</DriverText></View></View><DriverButton label="Switch to Passenger Mode" onPress={onSwitchToPassenger}/></DriverCard> : null}<DriverCard style={styles.readOnly}><MaterialCommunityIcons color={colors.primary} name="shield-lock-outline" size={27}/><View style={styles.readOnlyCopy}><DriverText weight="700">Verified account details</DriverText><DriverText color={colors.textSecondary} size={13}>Phone: {profile?.phone_number.replace(/\D/g,'').slice(-10) ?? '—'}</DriverText><DriverText color={colors.textSecondary} size={13}>Phone, vehicle, and documents can only be changed through support to preserve verification.</DriverText></View></DriverCard></>}</ScrollView></SafeAreaView>;
}

const styles = StyleSheet.create({ safe: { backgroundColor: colors.background, flex: 1 }, content: { gap: spacing.lg, padding: spacing.xl, paddingBottom: spacing.massive }, loading: { alignItems: 'center', gap: spacing.md, paddingVertical: spacing.massive }, card: { gap: spacing.lg }, modeCard: { gap: spacing.md }, modeIcon: { alignItems: 'center', backgroundColor: colors.primarySoft, borderRadius: 22, height: 44, justifyContent: 'center', width: 44 }, readOnly: { alignItems: 'flex-start', flexDirection: 'row', gap: spacing.md }, readOnlyCopy: { flex: 1, gap: spacing.xs } });
