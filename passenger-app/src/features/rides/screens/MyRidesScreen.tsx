import { SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { DsCard, DsEmptyState, DsLoading, DsText } from '../../../components/design-system';
import { AppPageHeader } from '../../../components/navigation/AppPageHeader';
import { colors, radius, spacing } from '../../../theme';
import type { RecentRide } from '../../home/domain/homeTypes';
import { usePassengerHome } from '../../home/state/usePassengerHome';

type MyRidesScreenProps = { onBack: () => void; onMenuPress: () => void };
const rideDetails = [{ driver: 'Arjun Kumar', vehicle: 'Car • Swift Dzire', icon: 'car' }, { driver: 'Ravi Patil', vehicle: 'Bike • Honda Shine', icon: 'motorbike' }, { driver: 'Suresh Naik', vehicle: 'Auto • Bajaj RE', icon: 'rickshaw' }];
/** Ride history reads the same recent-ride API as Home while extending each card with demo ride metadata. */
export function MyRidesScreen({ onBack, onMenuPress }: MyRidesScreenProps) {
  const { data, error, loading, refresh } = usePassengerHome();
  if (loading) return <SafeAreaView style={styles.safe}><DsLoading fullScreen label="Loading your rides…" /></SafeAreaView>;
  if (error || !data) return <SafeAreaView style={styles.safe}><DsEmptyState actionLabel="Try again" description={error ?? undefined} onAction={() => void refresh()} title="Unable to load rides" /></SafeAreaView>;
  return <SafeAreaView style={styles.safe}><ScrollView contentContainerStyle={styles.content}><AppPageHeader onBack={onBack} onMenuPress={onMenuPress} title="My Rides" /><DsText color={colors.textSecondary}>Your completed ride history</DsText>{data.recent_rides.length ? data.recent_rides.map((ride, index) => <RideHistoryCard detail={rideDetails[index % rideDetails.length]} key={ride.id} ride={ride} />) : <DsEmptyState title="No rides yet" description="Your completed rides will appear here." />}</ScrollView></SafeAreaView>;
}
function RideHistoryCard({ ride, detail }: { ride: RecentRide; detail: typeof rideDetails[number] }) { const date = ride.completed_at ? new Date(ride.completed_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'Recently'; return <DsCard elevated style={styles.card}><View style={styles.top}><View style={styles.vehicleIcon}><MaterialCommunityIcons color={colors.primary} name={detail.icon} size={25} /></View><View style={styles.copy}><DsText variant="h3">{ride.pickup_address} → {ride.destination_address}</DsText><DsText color={colors.textSecondary}>{date}</DsText></View><DsText color={colors.primary} variant="h2">₹ {ride.fare_paise / 100}</DsText></View><View style={styles.divider} /><View style={styles.bottom}><DsText color={colors.textSecondary}>{detail.driver}</DsText><DsText color={colors.textTertiary}>{detail.vehicle}</DsText></View></DsCard>; }
const styles = StyleSheet.create({ safe: { backgroundColor: colors.background, flex: 1 }, content: { gap: spacing.lg, padding: spacing.xl, paddingBottom: spacing.massive }, card: { gap: spacing.md }, top: { alignItems: 'center', flexDirection: 'row', gap: spacing.md }, copy: { flex: 1, gap: spacing.xxs }, vehicleIcon: { alignItems: 'center', backgroundColor: colors.primarySoft, borderColor: colors.primary, borderRadius: radius.sm, borderWidth: 1, height: 48, justifyContent: 'center', width: 48 }, divider: { backgroundColor: colors.border, height: 1 }, bottom: { flexDirection: 'row', justifyContent: 'space-between' } });
