import { useEffect, useState } from 'react';
import { SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import { AppPageHeader } from '../../../components/navigation/AppPageHeader';
import { DsButton, DsCard, DsEmptyState, DsLoading, DsText } from '../../../components/design-system';
import { colors, spacing } from '../../../theme';
import { bookingApi, type FareEstimate, type LocationOption, type RideBooking } from '../data/bookingApi';
import { VirgoMap } from '../../maps/components/VirgoMap';

type FareEstimateScreenProps = { pickup: LocationOption; destination: LocationOption; categoryId: number; onBack: () => void; onMenuPress: () => void; onBooked: (ride: RideBooking) => void };
export function FareEstimateScreen({ pickup, destination, categoryId, onBack, onMenuPress, onBooked }: FareEstimateScreenProps) {
  const [estimate, setEstimate] = useState<FareEstimate | null>(null); const [error, setError] = useState<string | null>(null); const [booking, setBooking] = useState(false);
  useEffect(() => { void bookingApi.estimate(pickup, destination, categoryId).then(setEstimate).catch(() => setError('Unable to calculate your fare.')); }, [pickup, destination, categoryId]);
  if (error) return <SafeAreaView style={styles.safe}><DsEmptyState actionLabel="Back" onAction={onBack} title={error} /></SafeAreaView>;
  if (!estimate) return <SafeAreaView style={styles.safe}><DsLoading fullScreen label="Calculating fare…" /></SafeAreaView>;
  const book = async () => { setBooking(true); try { onBooked(await bookingApi.book(pickup, destination, categoryId)); } catch (cause) { setError(cause instanceof Error ? cause.message : 'Unable to request a Driver right now. Please try again.'); } finally { setBooking(false); } };
  return <SafeAreaView style={styles.safe}><ScrollView contentContainerStyle={styles.content}><AppPageHeader onBack={onBack} onMenuPress={onMenuPress} title="Confirm your ride"/><VirgoMap destination={destination} pickup={pickup} route={estimate.route_geojson}/><DsCard elevated style={styles.route}><DsText color={colors.textTertiary}>Pickup</DsText><DsText variant="h3">{estimate.pickup.name}</DsText><View style={styles.line}/><DsText color={colors.textTertiary}>Destination</DsText><DsText variant="h3">{estimate.destination.name}</DsText></DsCard><DsCard elevated style={styles.summary}><DsText variant="h2">{estimate.category_name}</DsText><DsText color={colors.textSecondary}>{estimate.distance_km} km • {estimate.duration_minutes} min</DsText>{estimate.fare_items.map(item => <View key={item.label} style={styles.row}><DsText>{item.label}</DsText><DsText>₹ {item.amount_paise / 100}</DsText></View>)}<View style={styles.line}/><View style={styles.row}><DsText variant="h2">Estimated fare</DsText><DsText color={colors.primary} variant="h1">₹ {estimate.fare_paise / 100}</DsText></View></DsCard><DsButton label="Confirm ride" loading={booking} onPress={book} size="large"/></ScrollView></SafeAreaView>;
}
const styles = StyleSheet.create({ safe: { backgroundColor: colors.background, flex: 1 }, content: { gap: spacing.xl, padding: spacing.xl }, route: { gap: spacing.xs }, summary: { gap: spacing.md }, line: { backgroundColor: colors.border, height: 1, marginVertical: spacing.sm }, row: { flexDirection: 'row', justifyContent: 'space-between' } });
