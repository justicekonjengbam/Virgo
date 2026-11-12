import { useEffect, useState } from 'react';
import { ActivityIndicator, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DriverPageHeader } from '../../../components/DriverPageHeader';
import { DriverCard } from '../../../components/DriverCard';
import { DriverText } from '../../../components/DriverText';
import { colors, spacing } from '../../../theme';
import { driverMenuService, type DriverTrip } from '../../dashboard/services/driverMenuService';

export function DriverTripHistoryScreen({ onBack }: { onBack: () => void }) {
  const [trips, setTrips] = useState<DriverTrip[] | null>(null);
  useEffect(() => { void driverMenuService.getTripHistory().then(setTrips).catch(() => setTrips([])); }, []);
  return <SafeAreaView style={styles.safe}><DriverPageHeader onBack={onBack} title="Trip History"/><ScrollView contentContainerStyle={styles.content}>{trips === null ? <ActivityIndicator color={colors.primary} size="large"/> : trips.length === 0 ? <DriverCard style={styles.empty}><MaterialCommunityIcons color={colors.primary} name="history" size={42}/><DriverText size={19} weight="700">No completed trips yet</DriverText><DriverText color={colors.textSecondary} style={styles.center}>Your completed rides and final earnings will appear here.</DriverText></DriverCard> : trips.map(trip => <TripCard key={trip.id} trip={trip}/>)}</ScrollView></SafeAreaView>;
}
function TripCard({ trip }: { trip: DriverTrip }) { return <DriverCard style={styles.trip}><View style={styles.tripIcon}><MaterialCommunityIcons color={colors.primary} name="map-marker-path" size={25}/></View><View style={styles.tripCopy}><DriverText weight="700">{trip.pickup_address}</DriverText><DriverText color={colors.textSecondary}>to {trip.destination_address}</DriverText><DriverText color={colors.textSecondary} size={13}>{trip.category} • {trip.completed_at ? new Date(trip.completed_at).toLocaleDateString('en-IN') : 'Completed'}</DriverText></View><DriverText color={colors.primary} size={18} weight="700">₹{Math.round(trip.fare_paise / 100)}</DriverText></DriverCard>; }
const styles = StyleSheet.create({ safe: { backgroundColor: colors.background, flex: 1 }, content: { gap: spacing.md, padding: spacing.xl, paddingBottom: spacing.massive }, empty: { alignItems: 'center', gap: spacing.md, padding: spacing.xxl }, center: { textAlign: 'center' }, trip: { alignItems: 'center', flexDirection: 'row', gap: spacing.md, padding: spacing.md }, tripIcon: { alignItems: 'center', backgroundColor: colors.primarySoft, borderRadius: 12, height: 46, justifyContent: 'center', width: 46 }, tripCopy: { flex: 1, gap: spacing.xxs } });
