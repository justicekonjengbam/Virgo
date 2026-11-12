import { useEffect, useState } from 'react';
import { ActivityIndicator, Alert, Linking, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { AppPageHeader } from '../../../components/navigation/AppPageHeader';
import { DsButton, DsCard, DsText } from '../../../components/design-system';
import { colors, radius, spacing } from '../../../theme';
import { VirgoMap } from '../../maps/components/VirgoMap';
import { bookingApi, type RideBooking, type RideStatus } from '../data/bookingApi';
import { subscribeToRide, type DriverLocation } from '../services/passengerRealtimeService';

type Props = { ride: RideBooking; onDone: () => void; onMenuPress: () => void };

export function BookingStatusScreen({ ride, onDone, onMenuPress }: Props) {
  const [status, setStatus] = useState<RideStatus | null>(null);
  const [driverLocation, setDriverLocation] = useState<DriverLocation | null>(null);
  const [liveConnected, setLiveConnected] = useState(false);
  const [ending, setEnding] = useState(false);
  useEffect(() => subscribeToRide(ride.ride_id, setStatus, setLiveConnected, setDriverLocation), [ride.ride_id]);
  useEffect(() => {
    if (liveConnected) return;
    let mounted = true;
    const load = () => void bookingApi.status(ride.ride_id).then(value => { if (mounted) setStatus(value); }).catch(() => undefined);
    load(); const interval = setInterval(load, 10_000);
    return () => { mounted = false; clearInterval(interval); };
  }, [liveConnected, ride.ride_id]);
  const state = status?.status ?? ride.status;
  const finished = state === 'cancelled' || state === 'completed';
  const title = state === 'driver_arriving' ? 'Driver is on the way' : state === 'driver_arrived' ? 'Driver has arrived' : state === 'in_progress' ? 'Ride in progress' : state === 'completed' ? 'Ride completed' : state === 'cancelled' ? 'Ride ended' : 'Finding your driver';
  const icon = state === 'cancelled' ? 'car-off' : state === 'completed' ? 'check-decagram' : state === 'in_progress' ? 'navigation-variant' : state.startsWith('driver_') ? 'car-clock' : 'radar';
  const askToEnd = () => Alert.alert(status?.can_end ? 'End this active trip?' : 'Cancel this ride?', status?.can_end ? 'Use this only when the trip must stop early. The Driver and support records will be updated.' : 'The Driver will be notified immediately. Frequent late cancellations may be reviewed.', [{ text: 'Keep ride', style: 'cancel' }, { text: status?.can_end ? 'End ride' : 'Cancel ride', style: 'destructive', onPress: () => void endRide() }]);
  const endRide = async () => { setEnding(true); try { await bookingApi.cancel(ride.ride_id, status?.can_end ? 'Passenger ended trip early' : 'Passenger changed plans'); setStatus(await bookingApi.status(ride.ride_id)); } catch (cause) { Alert.alert('Ride not changed', cause instanceof Error ? cause.message : 'Please try again.'); } finally { setEnding(false); } };
  const pickup = status ? { latitude: status.pickup_latitude, longitude: status.pickup_longitude } : null;
  const destination = status ? { latitude: status.destination_latitude, longitude: status.destination_longitude } : null;
  const driver = driverLocation ?? (status?.driver_latitude != null && status.driver_longitude != null ? { latitude: status.driver_latitude, longitude: status.driver_longitude } : null);
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.content}>
        <AppPageHeader onBack={finished ? onDone : askToEnd} onMenuPress={onMenuPress} title="Your ride" />
        <VirgoMap destination={destination} driver={driver} pickup={pickup} route={status?.route_geojson} showUserLocation />
        <View style={styles.connection}>
          <View style={[styles.dot, { backgroundColor: liveConnected ? colors.success : colors.warning }]} />
          <DsText color={colors.textSecondary} variant="caption">
            {liveConnected ? 'Live tracking connected' : 'Reconnecting live tracking…'}
          </DsText>
        </View>
        <View style={styles.heading}>
          <View style={styles.icon}>
            <MaterialCommunityIcons
              color={state === 'cancelled' ? colors.error : state === 'completed' ? colors.success : colors.primary}
              name={icon}
              size={34}
            />
          </View>
          <View style={styles.headingCopy}>
            <DsText color={state === 'cancelled' ? colors.error : colors.primary} variant="h1">
              {title}
            </DsText>
            <DsText color={colors.textSecondary}>{status?.message ?? ride.message}</DsText>
          </View>
        </View>
        {status?.ride_start_otp ? (
          <DsCard elevated style={styles.otpCard}>
            <View style={styles.otpHeader}>
              <MaterialCommunityIcons color={colors.primary} name="shield-key" size={24} />
              <DsText color={colors.primary} variant="h3">
                Ride-Start PIN
              </DsText>
            </View>
            <DsText color={colors.textSecondary} variant="caption">
              Share this PIN with your driver to start your ride
            </DsText>
            <View style={styles.otpBadge}>
              <DsText color={colors.primary} style={styles.otpText} variant="h1">
                {status.ride_start_otp}
              </DsText>
            </View>
          </DsCard>
        ) : null}
        <DsCard elevated style={styles.card}>
          <RouteLine label="Pickup" value={ride.pickup_address} />
          <View style={styles.line} />
          <RouteLine label="Destination" value={ride.destination_address} />
          {status?.driver_name ? (
            <>
              <View style={styles.line} />
              <DsText variant="h3">{status.driver_name}</DsText>
              <DsText color={colors.textSecondary}>
                {status.vehicle_name} · {status.vehicle_registration_number}
              </DsText>
              {status.driver_arrival_minutes != null ? (
                <DsText color={colors.primary} variant="bodyMedium">
                  About {status.driver_arrival_minutes} min away
                </DsText>
              ) : null}
            </>
          ) : null}
        </DsCard>
        {state === 'cancelled' ? (
          <DsCard elevated style={styles.card}>
            <DsText color={colors.primary} variant="h3">
              Need a ride right now?
            </DsText>
            <DsText color={colors.textSecondary}>
              Call our Virgo Imphal dispatch team directly for instant booking support.
            </DsText>
            <DsButton
              label="Call &amp; Book (+91 6009060341)"
              onPress={() => void Linking.openURL('tel:+916009060341')}
            />
          </DsCard>
        ) : null}
        {!status && !finished ? <ActivityIndicator color={colors.primary} /> : null}
        {finished ? (
          <DsButton label="Back to Home" onPress={onDone} />
        ) : status?.can_cancel || status?.can_end ? (
          <DsButton
            label={status.can_end ? 'End ride early' : 'Cancel ride'}
            loading={ending}
            onPress={askToEnd}
            variant="secondary"
          />
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

function RouteLine({ label, value }: { label: string; value: string }) { return <View style={styles.routeLine}><DsText color={colors.textTertiary} variant="caption">{label}</DsText><DsText variant="h3">{value}</DsText></View>; }
const styles = StyleSheet.create({ safe: { backgroundColor: colors.background, flex: 1 }, content: { gap: spacing.lg, padding: spacing.xl, paddingBottom: spacing.massive }, connection: { alignItems: 'center', flexDirection: 'row', gap: spacing.sm }, dot: { borderRadius: radius.pill, height: 8, width: 8 }, heading: { alignItems: 'center', flexDirection: 'row', gap: spacing.md }, headingCopy: { flex: 1, gap: spacing.xs }, icon: { alignItems: 'center', backgroundColor: colors.primarySoft, borderRadius: radius.pill, height: 58, justifyContent: 'center', width: 58 }, card: { gap: spacing.md }, routeLine: { gap: spacing.xs }, line: { backgroundColor: colors.border, height: 1 }, otpCard: { alignItems: 'center', backgroundColor: colors.surface, borderColor: colors.primary, borderRadius: radius.lg, borderWidth: 1.5, gap: spacing.xs, padding: spacing.lg }, otpHeader: { alignItems: 'center', flexDirection: 'row', gap: spacing.xs }, otpBadge: { backgroundColor: colors.primarySoft, borderRadius: radius.md, marginTop: spacing.xs, paddingHorizontal: spacing.xl, paddingVertical: spacing.sm }, otpText: { letterSpacing: 8 } });
