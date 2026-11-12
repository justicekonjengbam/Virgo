import { useEffect, useState } from 'react';
import { Alert, Pressable, SafeAreaView, ScrollView, StyleSheet, TextInput, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DriverButton } from '../../../components/DriverButton';
import { DriverCard } from '../../../components/DriverCard';
import { DriverPageHeader } from '../../../components/DriverPageHeader';
import { DriverText } from '../../../components/DriverText';
import { colors, radius, spacing, typography } from '../../../theme';
import { DriverRideMap } from '../../maps/components/DriverRideMap';
import { useDriverLocationReporter } from '../../maps/hooks/useDriverLocationReporter';
import { driverRealtimeService } from '../services/driverRealtimeService';
import { rideMatchingService, type DriverActiveRide, type RideSummary } from '../services/rideMatchingService';

export function DriverActiveRideScreen({ onBack, onFinished }: { onBack: () => void; onFinished: () => void }) {
  const [ride, setRide] = useState<DriverActiveRide | null>(null);
  const [message, setMessage] = useState('Loading active ride…');
  const [updating, setUpdating] = useState(false);
  const [startOtp, setStartOtp] = useState('');
  const [summary, setSummary] = useState<RideSummary | null>(null);
  const { permissionDenied } = useDriverLocationReporter(true);
  const refresh = () => void rideMatchingService.activeRide().then(value => { setRide(value); setMessage(value ? '' : 'You do not have an active ride.'); }).catch(() => setMessage('Unable to load the active ride.'));
  useEffect(refresh, []);
  useEffect(() => driverRealtimeService.subscribe(event => { if (event.type === 'ride.cancelled' || event.type === 'ride.completed') { setRide(null); setMessage(event.type === 'ride.cancelled' ? 'This ride was cancelled.' : 'This ride is complete.'); } else if (event.type.startsWith('ride.')) refresh(); }), []);
  const action = async (next: 'arrived' | 'start' | 'complete') => { if (!ride) return; if (next === 'start' && !/^\d{4}$/.test(startOtp)) { Alert.alert('Enter ride-start OTP', 'Ask the passenger for the 4-digit OTP shown in their app.'); return; } setUpdating(true); try { await rideMatchingService.action(ride.ride_id, next, next === 'start' ? startOtp : undefined); if (next === 'complete') setSummary(await rideMatchingService.summary(ride.ride_id)); else refresh(); } catch (cause) { Alert.alert('Unable to update ride', cause instanceof Error ? cause.message : 'Please try again.'); } finally { setUpdating(false); } };
  const askToEnd = () => ride && Alert.alert(ride.can_end ? 'End this trip early?' : 'Cancel this pickup?', ride.can_end ? 'Use this only when the trip cannot safely continue. Support records will preserve the reason.' : 'The passenger will be notified immediately. Avoid cancelling after accepting unless necessary.', [{ text: 'Keep ride', style: 'cancel' }, { text: ride.can_end ? 'End trip' : 'Cancel pickup', style: 'destructive', onPress: () => void cancel() }]);
  const cancel = async () => { if (!ride) return; const reason = ride.can_end ? 'vehicle_issue' : ride.status === 'driver_arrived' ? 'passenger_no_show' : 'vehicle_issue'; setUpdating(true); try { await rideMatchingService.cancel(ride.ride_id, reason); Alert.alert('Ride ended', 'The passenger has been notified.', [{ text: 'Done', onPress: onFinished }]); } catch (cause) { Alert.alert('Unable to end ride', cause instanceof Error ? cause.message : 'Please try again.'); } finally { setUpdating(false); } };
  const rate = async (score: number) => { if (!summary) return; setUpdating(true); try { await rideMatchingService.rate(summary.ride_id, score); Alert.alert('Rating submitted', 'Thank you for rating the passenger.', [{ text: 'Done', onPress: onFinished }]); } catch (cause) { Alert.alert('Unable to submit rating', cause instanceof Error ? cause.message : 'Please try again.'); } finally { setUpdating(false); } };
  const [paymentCollected, setPaymentCollected] = useState(false);
  const confirmPayment = async (method: 'cash' | 'upi') => {
    if (!summary) return;
    setUpdating(true);
    try {
      await rideMatchingService.action(summary.ride_id, 'confirm_payment', undefined, method);
      setPaymentCollected(true);
      Alert.alert('Payment Recorded', `Payment of ₹${Math.round(summary.fare_paise / 100)} collected via ${method.toUpperCase()}.`);
    } catch (cause) {
      Alert.alert('Payment error', cause instanceof Error ? cause.message : 'Please try again.');
    } finally {
      setUpdating(false);
    }
  };

  if (summary) {
    const isCollected = paymentCollected || summary.payment_status === 'completed';
    return (
      <SafeAreaView style={styles.safe}>
        <ScrollView contentContainerStyle={styles.content}>
          <DriverPageHeader onBack={onFinished} title="Fare Summary" />
          <DriverCard style={styles.card}>
            <DriverText size={22} weight="700">Ride completed</DriverText>
            <DriverText color={colors.textSecondary}>{summary.distance_km} km · {summary.duration_minutes} min</DriverText>
            {summary.fare_items.map(item => (
              <View key={item.label} style={styles.summaryRow}>
                <DriverText>{item.label}</DriverText>
                <DriverText>₹{Math.round(item.amount_paise / 100)}</DriverText>
              </View>
            ))}
            <View style={styles.line} />
            <View style={styles.summaryRow}>
              <DriverText size={18} weight="700">Customer Fare</DriverText>
              <DriverText color={colors.primary} size={20} weight="700">₹{Math.round(summary.fare_paise / 100)}</DriverText>
            </View>
            {summary.commission_paise != null ? (
              <View style={styles.summaryRow}>
                <DriverText color={colors.textSecondary}>Virgo Commission (10%)</DriverText>
                <DriverText color={colors.textSecondary}>-₹{Math.round(summary.commission_paise / 100)}</DriverText>
              </View>
            ) : null}
            {summary.driver_net_paise != null ? (
              <View style={styles.summaryRow}>
                <DriverText size={18} weight="700" color={colors.success}>Your Net Earnings</DriverText>
                <DriverText color={colors.success} size={22} weight="700">₹{Math.round(summary.driver_net_paise / 100)}</DriverText>
              </View>
            ) : null}
          </DriverCard>

          <DriverCard style={styles.card}>
            <DriverText size={18} weight="700">Payment Collection</DriverText>
            {isCollected ? (
              <View style={[styles.summaryRow, { backgroundColor: '#ebf8f1', padding: spacing.sm, borderRadius: radius.md }]}>
                <DriverText color={colors.success} weight="700">Payment Collected ✓</DriverText>
                <DriverText color={colors.success}>₹{Math.round(summary.fare_paise / 100)}</DriverText>
              </View>
            ) : (
              <View style={{ gap: spacing.sm }}>
                <DriverText color={colors.textSecondary}>Collect full fare amount from passenger before leaving:</DriverText>
                <View style={{ flexDirection: 'row', gap: spacing.md }}>
                  <DriverButton
                    label="Collect Cash"
                    loading={updating}
                    onPress={() => void confirmPayment('cash')}
                  />
                  <DriverButton
                    label="Collect UPI"
                    loading={updating}
                    onPress={() => void confirmPayment('upi')}
                    variant="secondary"
                  />
                </View>
              </View>
            )}
          </DriverCard>

          <DriverCard style={styles.card}>
            <DriverText size={18} weight="700">Rate your passenger</DriverText>
            <View style={styles.stars}>
              {[1, 2, 3, 4, 5].map(score => (
                <Pressable accessibilityLabel={`Rate ${score} stars`} key={score} onPress={() => void rate(score)}>
                  <MaterialCommunityIcons color={colors.primary} name="star-outline" size={36} />
                </Pressable>
              ))}
            </View>
          </DriverCard>
          <DriverButton label="Done" onPress={onFinished} />
        </ScrollView>
      </SafeAreaView>
    );
  }
  if (!ride) return <SafeAreaView style={styles.safe}><DriverPageHeader onBack={onBack} title="Active Ride" /><View style={styles.empty}><MaterialCommunityIcons color={colors.textTertiary} name="car-off" size={42} /><DriverText color={colors.textSecondary}>{message}</DriverText><DriverButton label="Back to Home" onPress={onFinished} /></View></SafeAreaView>;
  const nextAction = ride.status === 'driver_arriving' ? ['I have arrived', 'arrived'] as const : ride.status === 'driver_arrived' ? ['Start ride', 'start'] as const : ['Complete ride', 'complete'] as const;
  return <SafeAreaView style={styles.safe}><ScrollView contentContainerStyle={styles.content}><DriverPageHeader onBack={onBack} title="Active Ride" /><DriverRideMap destination={{ latitude: ride.destination_latitude, longitude: ride.destination_longitude }} pickup={{ latitude: ride.pickup_latitude, longitude: ride.pickup_longitude }} route={ride.route_geojson} />{permissionDenied ? <DriverCard style={styles.warning}><MaterialCommunityIcons color={colors.warning} name="crosshairs-question" size={24} /><DriverText color={colors.textSecondary} style={styles.warningCopy}>Allow precise location so the passenger can see your arrival.</DriverText></DriverCard> : null}<DriverCard style={styles.card}><DriverText color={colors.primary} size={18} weight="700">{ride.passenger_name}</DriverText><RouteRow label="Pickup" value={ride.pickup_address} /><View style={styles.line} /><RouteRow label="Destination" value={ride.destination_address} /></DriverCard>{ride.status === 'driver_arrived' ? <DriverCard style={styles.card}><DriverText weight="700">Ride-start OTP</DriverText><DriverText color={colors.textSecondary} size={13}>Ask the passenger for their 4-digit OTP before starting.</DriverText><TextInput keyboardType="number-pad" maxLength={4} onChangeText={setStartOtp} placeholder="Enter 4-digit OTP" placeholderTextColor={colors.textTertiary} style={styles.otp} value={startOtp} /></DriverCard> : null}<DriverButton label={nextAction[0]} loading={updating} onPress={() => void action(nextAction[1])} /><DriverButton label={ride.can_end ? 'End ride early' : 'Cancel accepted ride'} disabled={updating} onPress={askToEnd} variant="secondary" /></ScrollView></SafeAreaView>;
}

function RouteRow({ label, value }: { label: string; value: string }) { return <View style={styles.route}><DriverText color={colors.textTertiary} size={12}>{label}</DriverText><DriverText size={17} weight="600">{value}</DriverText></View>; }
const styles = StyleSheet.create({ safe: { backgroundColor: colors.background, flex: 1 }, content: { gap: spacing.lg, padding: spacing.xl, paddingBottom: spacing.massive }, empty: { alignItems: 'center', flex: 1, gap: spacing.lg, justifyContent: 'center', padding: spacing.xl }, card: { gap: spacing.md, padding: spacing.lg }, route: { gap: spacing.xs }, line: { backgroundColor: colors.border, height: 1 }, warning: { alignItems: 'center', backgroundColor: colors.warningSoft, flexDirection: 'row', gap: spacing.sm, padding: spacing.md }, warningCopy: { flex: 1 }, otp: { borderColor: colors.primary, borderRadius: radius.md, borderWidth: 1, color: colors.textPrimary, fontFamily: typography.family.medium, fontSize: 20, letterSpacing: 8, minHeight: 54, paddingHorizontal: spacing.md }, summaryRow: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between' }, stars: { flexDirection: 'row', justifyContent: 'space-between' } });
