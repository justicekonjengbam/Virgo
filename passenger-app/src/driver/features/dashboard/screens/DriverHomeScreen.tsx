import { useCallback, useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Alert, AppState, Modal, Pressable, RefreshControl, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DriverCard } from '../../../components/DriverCard';
import { DriverText } from '../../../components/DriverText';
import { colors, radius, shadows, spacing } from '../../../theme';
import { DriverDrawer } from '../components/DriverDrawer';
import { DriverHeader } from '../components/DriverHeader';
import { useDriverDashboard } from '../hooks/useDriverDashboard';
import type { DriverDashboard, DriverVehicleStatus } from '../services/driverDashboardService';
import { useDriverSession } from '../state/DriverSessionContext';
import { rideMatchingService } from '../../rides/services/rideMatchingService';
import { driverRealtimeService } from '../../rides/services/driverRealtimeService';
import { useDriverLocationReporter } from '../../maps/hooks/useDriverLocationReporter';

type DriverHomeScreenProps = { onOpenActiveRide: () => void; onOpenDocuments: () => void; onOpenEarnings: () => void; onOpenHelp: () => void; onOpenOutstation: () => void; onOpenRequest: () => void; onOpenSettings: () => void; onOpenTripHistory: () => void; onLogout: () => void; onSwitchToPassenger?: () => void };
type DetailSheet = 'earnings' | 'history' | 'vehicle' | null;

export function DriverHomeScreen({ onOpenActiveRide, onOpenDocuments, onOpenEarnings, onOpenHelp, onOpenOutstation, onOpenRequest, onOpenSettings, onOpenTripHistory, onLogout, onSwitchToPassenger }: DriverHomeScreenProps) {
  const session = useDriverSession();
  const { dashboard, error, isLoading, isRefreshing, refresh, updateAvailability } = useDriverDashboard();
  const [menuVisible, setMenuVisible] = useState(false);
  const [sheet, setSheet] = useState<DetailSheet>(null);
  const [updatingAvailability, setUpdatingAvailability] = useState(false);
  const [hasPendingOffer, setHasPendingOffer] = useState(false);
  const [liveConnected, setLiveConnected] = useState(false);
  const [activeRideId, setActiveRideId] = useState<number | null>(null);
  const { permissionDenied } = useDriverLocationReporter(session.isOnline);
  const handledOfferIdRef = useRef<number | null>(null);

  const handleIncomingOffer = useCallback((offerId: number) => {
    setHasPendingOffer(true);
    if (handledOfferIdRef.current !== offerId) {
      handledOfferIdRef.current = offerId;
      onOpenRequest();
    }
  }, [onOpenRequest]);

  useEffect(() => {
    if (dashboard) session.setIsOnline(dashboard.is_online);
  }, [dashboard, session]);

  useEffect(() => {
    return driverRealtimeService.subscribe(
      event => {
        if (event.type === 'outstation.assigned') {
          Alert.alert('Outstation trip scheduled', `Virgo Support assigned booking #${event.data.booking_id} to you. Review the route and departure details now.`, [{ text:'Later', style:'cancel' }, { text:'View schedule', onPress:onOpenOutstation }]);
          return;
        }
        if (event.type === 'outstation.updated') {
          if (event.data.status === 'completed') Alert.alert('Outstation trip completed', `Booking #${event.data.booking_id} has been moved to your completed trips.`);
          return;
        }
        if (event.type === 'ride.offer') {
          handleIncomingOffer(event.data.offer_id);
        } else if (event.type === 'ride.offer_cleared') {
          setHasPendingOffer(false);
          handledOfferIdRef.current = null;
        }
      },
      setLiveConnected,
    );
  }, [handleIncomingOffer, onOpenOutstation]);

  useEffect(() => {
    let isMounted = true;
    const syncOffer = async () => {
      try {
        const offer = await rideMatchingService.getCurrentOffer();
        if (!isMounted) return;
        if (offer) {
          handleIncomingOffer(offer.offer_id);
        } else {
          setHasPendingOffer(false);
          handledOfferIdRef.current = null;
        }
      } catch {
        // Ignore transient poll failures
      }
    };

    void syncOffer();
    const interval = setInterval(syncOffer, 4_000);

    const subscription = AppState.addEventListener('change', nextAppState => {
      if (nextAppState === 'active') {
        void syncOffer();
      }
    });

    return () => {
      isMounted = false;
      clearInterval(interval);
      subscription.remove();
    };
  }, [handleIncomingOffer]);

  useEffect(() => {
    const load = () => void rideMatchingService.activeRide().then(ride => setActiveRideId(ride?.ride_id ?? null)).catch(() => undefined);
    load(); const interval = setInterval(load, 10_000);
    return () => clearInterval(interval);
  }, []);

  const toggleAvailability = async () => {
    if (updatingAvailability) return;
    setUpdatingAvailability(true);
    try {
      const updated = await updateAvailability(!session.isOnline);
      session.setIsOnline(updated.is_online);
    } finally {
      setUpdatingAvailability(false);
    }
  };

  const quickActions = [
    ['wallet-outline', 'Earnings', onOpenEarnings],
    ['file-document-outline', 'Documents', onOpenDocuments],
    ['history', 'History', onOpenTripHistory],
    ['car-outline', 'My Vehicle', () => setSheet('vehicle')],
    ['cog-outline', 'More', () => setMenuVisible(true)],
  ] as const;

  if (isLoading && !dashboard) return <DashboardLoading/>;
  if (!dashboard) return <DashboardError onRetry={() => void refresh()} />;

  const hasPendingRequest = session.isOnline && hasPendingOffer;
  return <SafeAreaView style={styles.safe}><ScrollView contentContainerStyle={styles.content} refreshControl={<RefreshControl colors={[colors.primary]} onRefresh={() => void refresh(true)} refreshing={isRefreshing}/>} showsVerticalScrollIndicator={false}>
    <DriverHeader fullName={dashboard.full_name} onMenuPress={() => setMenuVisible(true)} onRequestPress={onOpenRequest}/>
    {error ? <DriverCard style={styles.errorBanner}><MaterialCommunityIcons color={colors.danger} name="cloud-alert-outline" size={22}/><DriverText color={colors.textSecondary} size={13} style={styles.errorText}>{error}</DriverText><Pressable onPress={() => void refresh(true)}><DriverText color={colors.primary} size={13} weight="600">Retry</DriverText></Pressable></DriverCard> : null}
    <AvailabilityCard isOnline={session.isOnline} isUpdating={updatingAvailability} onToggle={() => void toggleAvailability()}/>
    {permissionDenied && session.isOnline ? <DriverCard style={styles.errorBanner}><MaterialCommunityIcons color={colors.warning} name="crosshairs-question" size={22}/><DriverText color={colors.textSecondary} size={13} style={styles.errorText}>Precise location is required to receive nearby rides.</DriverText></DriverCard> : null}
    {activeRideId ? <Pressable accessibilityRole="button" onPress={onOpenActiveRide} style={({ pressed }) => [pressed && styles.pressed]}><DriverCard style={styles.requestBanner}><View style={styles.requestIcon}><MaterialCommunityIcons color={colors.primary} name="navigation-variant" size={28}/></View><View style={styles.requestCopy}><DriverText weight="700">Continue active ride #{activeRideId}</DriverText><DriverText color={colors.textSecondary} size={13}>Open pickup tracking and ride controls.</DriverText></View><MaterialCommunityIcons color={colors.primary} name="chevron-right" size={24}/></DriverCard></Pressable> : null}
    <EarningsCard dashboard={dashboard}/>
    <PerformanceStats dashboard={dashboard}/>
    {hasPendingRequest ? (
      <Pressable accessibilityRole="button" onPress={onOpenRequest} style={({ pressed }) => [pressed && styles.pressed]}>
        <DriverCard style={styles.requestBanner}>
          <View style={styles.requestIcon}>
            <MaterialCommunityIcons color={colors.primary} name="car-clock" size={28} />
          </View>
          <View style={styles.requestCopy}>
            <DriverText weight="600">New ride request available</DriverText>
            <DriverText color={colors.textSecondary} size={13}>Tap to review pickup, drop, fare, and distance.</DriverText>
          </View>
          <MaterialCommunityIcons color={colors.primary} name="chevron-right" size={24} />
        </DriverCard>
      </Pressable>
    ) : session.isOnline ? (
      <DriverCard style={styles.waitingCard}>
        <View style={styles.waitingIcon}>
          <MaterialCommunityIcons color={colors.primary} name="radar" size={26} />
        </View>
        <View style={styles.waitingCopy}>
          <DriverText color={colors.primary} size={16} weight="700">Waiting for ride requests</DriverText>
          <DriverText color={colors.textSecondary} size={13}>You are online. Ready to receive rides in your area.</DriverText>
        </View>
        <ActivityIndicator color={colors.primary} size="small" />
      </DriverCard>
    ) : (
      <DriverCard style={styles.noRequest}>
        <MaterialCommunityIcons color={colors.textTertiary} name="power-standby" size={24} />
        <DriverText color={colors.textSecondary} style={styles.noRequestText}>
          You are currently offline. Turn on your status above to receive ride requests.
        </DriverText>
      </DriverCard>
    )}
    <DriverText size={24} weight="600">Vehicle Status</DriverText>
    <Pressable accessibilityRole="button" onPress={() => setSheet('vehicle')} style={({ pressed }) => [pressed && styles.pressed]}><VehicleCard vehicle={dashboard.vehicle}/></Pressable>
    <View style={styles.sectionHeading}><DriverText size={24} weight="600">Quick Actions</DriverText><Pressable accessibilityRole="button" onPress={() => setMenuVisible(true)}><DriverText color={colors.textSecondary}>See all</DriverText></Pressable></View>
    <View style={styles.quickActions}>{quickActions.map(([icon, label, onPress]) => <QuickAction icon={icon} key={label} label={label} onPress={onPress}/>)}</View>
    <DriverCard style={styles.shiftCard}><MaterialCommunityIcons color={colors.primary} name="calendar-clock-outline" size={28}/><View style={styles.shiftCopy}><DriverText weight="600">Today’s driving summary</DriverText><DriverText color={colors.textSecondary} size={13}>{summaryText(dashboard)}</DriverText></View></DriverCard>
    <DriverText color={colors.textTertiary} size={12} style={styles.version}>Virgo Driver • Happy Cabbing • Version 0.0.1</DriverText>
  </ScrollView><DriverDrawer onClose={() => setMenuVisible(false)} onOpenDocuments={onOpenDocuments} onOpenEarnings={onOpenEarnings} onOpenHelp={onOpenHelp} onOpenOutstation={onOpenOutstation} onOpenRideRequest={onOpenRequest} onOpenSettings={onOpenSettings} onOpenTripHistory={onOpenTripHistory} onSignOut={onLogout} onSwitchToPassenger={onSwitchToPassenger} visible={menuVisible}/><DriverDetailSheet dashboard={dashboard} onClose={() => setSheet(null)} onOpenDocuments={onOpenDocuments} type={sheet}/></SafeAreaView>;
}

function DashboardLoading() { return <SafeAreaView style={styles.centered}><ActivityIndicator color={colors.primary} size="large"/><DriverText color={colors.textSecondary}>Loading your driver dashboard…</DriverText></SafeAreaView>; }
function DashboardError({ onRetry }: { onRetry: () => void }) { return <SafeAreaView style={styles.centered}><MaterialCommunityIcons color={colors.danger} name="cloud-alert-outline" size={40}/><DriverText size={20} weight="600">Dashboard unavailable</DriverText><DriverText color={colors.textSecondary} style={styles.centeredCopy}>We could not load your current driver information.</DriverText><Pressable onPress={onRetry} style={styles.retryButton}><DriverText color={colors.white} weight="700">Try again</DriverText></Pressable></SafeAreaView>; }

function AvailabilityCard({ isOnline, isUpdating, onToggle }: { isOnline: boolean; isUpdating: boolean; onToggle: () => void }) { return <DriverCard style={styles.availability}><View style={[styles.power, !isOnline && styles.powerOffline]}><MaterialCommunityIcons color={colors.white} name="power" size={28}/></View><View style={styles.availabilityCopy}><DriverText size={21}>You are <DriverText color={isOnline ? colors.primary : colors.textSecondary} size={21} weight="600">{isOnline ? 'Online' : 'Offline'}</DriverText></DriverText><DriverText color={colors.textSecondary} size={13}>{isOnline ? 'All set to receive ride requests' : 'Go online to receive ride requests'}</DriverText></View><Pressable accessibilityRole="switch" accessibilityState={{ checked: isOnline, disabled: isUpdating }} disabled={isUpdating} onPress={onToggle} style={[styles.statusButton, !isOnline && styles.statusButtonOffline]}>{isUpdating ? <ActivityIndicator color={colors.primary} size="small"/> : <DriverText color={isOnline ? colors.primary : colors.textSecondary} size={13} weight="600">Go {isOnline ? 'Offline' : 'Online'}</DriverText>}</Pressable></DriverCard>; }

function EarningsCard({ dashboard }: { dashboard: DriverDashboard }) { return <View style={styles.earnings}><EarningColumn amount={dashboard.today_earnings_paise} label="Today" rides={dashboard.today_completed_rides}/><View style={styles.earningsDivider}/><EarningColumn amount={dashboard.month_earnings_paise} label="This month" rides={dashboard.month_completed_rides}/></View>; }
function EarningColumn({ amount, label, rides }: { amount: number; label: string; rides: number }) { return <View style={styles.earningColumn}><DriverText color={colors.white}>{label} earnings</DriverText><DriverText color={colors.white} size={31} weight="700">{formatRupees(amount)}</DriverText><DriverText color={colors.white} size={13}>{rides} {rides === 1 ? 'ride' : 'rides'} completed</DriverText></View>; }

function PerformanceStats({ dashboard }: { dashboard: DriverDashboard }) { const stats = [['clock-outline', 'Active time', formatMinutes(dashboard.online_minutes)], ['shield-check-outline', 'Safety score', dashboard.safety_score === null ? '—' : `${dashboard.safety_score}%`], ['star-outline', 'Rating', dashboard.rating === null ? 'New' : dashboard.rating.toFixed(1)]] as const; return <DriverCard style={styles.performance}>{stats.map(([icon, label, value], index) => <View accessibilityLabel={`${label}: ${value}`} key={label} style={[styles.performanceItem, index < stats.length - 1 && styles.performanceDivider]}><View style={styles.metricIcon}><MaterialCommunityIcons color={colors.primary} name={icon} size={22}/></View><DriverText color={colors.primary} size={14} style={styles.performanceValue} weight="700">{value}</DriverText></View>)}</DriverCard>; }

function VehicleCard({ vehicle }: { vehicle: DriverVehicleStatus | null }) { if (!vehicle) return <DriverCard style={styles.vehicle}><View style={styles.vehiclePlaceholder}><MaterialCommunityIcons color={colors.primary} name="car-off" size={42}/></View><View style={styles.vehicleCopy}><DriverText size={18} weight="600">No active vehicle</DriverText><DriverText color={colors.textSecondary}>Complete vehicle onboarding to receive rides.</DriverText></View></DriverCard>; const status = vehicle.verification_status === 'verified' ? 'Documents approved' : vehicle.verification_status === 'pending' ? 'Documents under review' : vehicle.verification_status === 'expired' ? 'Verification expired' : 'Verification needs attention'; return <DriverCard style={styles.vehicle}><View style={styles.vehiclePlaceholder}><MaterialCommunityIcons color={colors.primary} name={vehicle.category === 'bike' ? 'motorbike' : vehicle.category === 'auto' ? 'rickshaw' : 'car'} size={48}/></View><View style={styles.vehicleCopy}><DriverText size={20} weight="600">{capitalize(vehicle.category)}</DriverText><DriverText color={colors.primary} size={17} weight="700">{vehicle.make} {vehicle.model}</DriverText><DriverText color={colors.textSecondary}>{vehicle.registration_number} • {vehicle.seat_count} seats</DriverText><DriverText color={vehicle.verification_status === 'verified' ? colors.success : colors.textSecondary} weight="700">{status}</DriverText></View><MaterialCommunityIcons color={vehicle.verification_status === 'verified' ? colors.success : colors.primary} name={vehicle.verification_status === 'verified' ? 'check-circle' : 'clock-outline'} size={22}/></DriverCard>; }

function QuickAction({ icon, label, onPress }: { icon: string; label: string; onPress: () => void }) { return <Pressable accessibilityLabel={label} accessibilityRole="button" onPress={onPress} style={({ pressed }) => [styles.quickAction, pressed && styles.pressed]}><MaterialCommunityIcons color={colors.primary} name={icon} size={28}/><DriverText size={11} style={styles.quickActionLabel}>{label}</DriverText></Pressable>; }

function DriverDetailSheet({ dashboard, type, onClose, onOpenDocuments }: { dashboard: DriverDashboard; type: DetailSheet; onClose: () => void; onOpenDocuments: () => void }) { if (!type) return null; const vehicle = dashboard.vehicle; const copy = type === 'earnings' ? ['Earnings overview', `Today: ${formatRupees(dashboard.today_earnings_paise)}`, `This month: ${formatRupees(dashboard.month_earnings_paise)}`] : type === 'history' ? ['Ride history', dashboard.month_completed_rides ? `${dashboard.month_completed_rides} completed rides this month` : 'No completed rides yet', 'Your completed trips will appear here.'] : ['Vehicle details', vehicle ? `${vehicle.make} ${vehicle.model}` : 'No active vehicle', vehicle ? `${vehicle.registration_number} • ${vehicle.seat_count} seats` : '']; return <Modal animationType="slide" onRequestClose={onClose} transparent visible><Pressable onPress={onClose} style={styles.sheetOverlay}><Pressable onPress={() => undefined} style={styles.sheet}><View style={styles.sheetHandle}/><DriverText size={22} weight="700">{copy[0]}</DriverText><DriverText color={colors.textSecondary}>{copy[1]}</DriverText><DriverText color={colors.textSecondary}>{copy[2]}</DriverText>{type === 'vehicle' ? <Pressable accessibilityRole="button" onPress={() => { onClose(); onOpenDocuments(); }} style={[styles.sheetClose, { backgroundColor: colors.primary, borderColor: colors.primary }]}><DriverText color={colors.white} weight="600">View Document Compliance</DriverText></Pressable> : null}<Pressable accessibilityRole="button" onPress={onClose} style={styles.sheetClose}><DriverText color={colors.primary} weight="600">Close</DriverText></Pressable></Pressable></Pressable></Modal>; }

function formatRupees(paise: number) { return `₹${Math.round(paise / 100).toLocaleString('en-IN')}`; }
function formatMinutes(minutes: number) { return minutes < 60 ? `${minutes} min` : `${Math.floor(minutes / 60)} hr ${minutes % 60} min`; }
function capitalize(value: string) { return value.charAt(0).toUpperCase() + value.slice(1); }
function summaryText(dashboard: DriverDashboard) { return dashboard.today_completed_rides ? `You completed ${dashboard.today_completed_rides} ${dashboard.today_completed_rides === 1 ? 'ride' : 'rides'} and earned ${formatRupees(dashboard.today_earnings_paise)} today.` : 'No completed rides yet today. Go online when you are ready.'; }

const styles = StyleSheet.create({ safe: { backgroundColor: colors.background, flex: 1 }, content: { gap: spacing.lg, padding: spacing.xl, paddingBottom: spacing.massive }, centered: { alignItems: 'center', backgroundColor: colors.background, flex: 1, gap: spacing.md, justifyContent: 'center', padding: spacing.xl }, centeredCopy: { textAlign: 'center' }, retryButton: { alignItems: 'center', backgroundColor: colors.primary, borderRadius: radius.md, minWidth: 140, paddingHorizontal: spacing.lg, paddingVertical: spacing.md }, errorBanner: { alignItems: 'center', backgroundColor: colors.dangerSoft, flexDirection: 'row', gap: spacing.sm, padding: spacing.md }, errorText: { flex: 1 }, availability: { alignItems: 'center', flexDirection: 'row', gap: spacing.md, padding: spacing.md }, power: { alignItems: 'center', backgroundColor: colors.primary, borderRadius: radius.pill, height: 58, justifyContent: 'center', width: 58 }, powerOffline: { backgroundColor: colors.textTertiary }, availabilityCopy: { flex: 1, gap: spacing.xxs }, statusButton: { alignItems: 'center', borderColor: colors.primary, borderRadius: radius.sm, borderWidth: 1, minHeight: 42, justifyContent: 'center', minWidth: 102, paddingHorizontal: spacing.md, paddingVertical: spacing.sm }, statusButtonOffline: { borderColor: colors.textSecondary }, earnings: { ...shadows.raised, backgroundColor: colors.primary, borderRadius: radius.lg, flexDirection: 'row', gap: spacing.md, padding: spacing.lg }, earningColumn: { flex: 1, gap: spacing.md }, earningsDivider: { backgroundColor: 'rgba(255,255,255,0.5)', width: 1 }, performance: { alignItems: 'stretch', flexDirection: 'row', minHeight: 84, paddingHorizontal: spacing.sm, paddingVertical: spacing.sm }, performanceItem: { alignItems: 'center', flex: 1, gap: spacing.xs, justifyContent: 'center', minWidth: 0, paddingHorizontal: spacing.sm }, performanceDivider: { borderRightColor: colors.borderStrong, borderRightWidth: 1 }, performanceValue: { textAlign: 'center' }, metricIcon: { alignItems: 'center', borderColor: colors.primary, borderRadius: radius.sm, borderWidth: 1, height: 36, justifyContent: 'center', width: 36 }, requestBanner: { alignItems: 'center', flexDirection: 'row', gap: spacing.sm, padding: spacing.md }, requestIcon: { alignItems: 'center', backgroundColor: colors.primarySoft, borderRadius: radius.sm, height: 50, justifyContent: 'center', width: 50 }, requestCopy: { flex: 1, gap: spacing.xxs }, noRequest: { alignItems: 'center', backgroundColor: colors.successSoft, flexDirection: 'row', gap: spacing.sm, padding: spacing.md }, noRequestText: { flex: 1 }, waitingCard: { alignItems: 'center', backgroundColor: colors.primarySoft, borderColor: colors.primary, borderRadius: radius.md, borderWidth: 1, flexDirection: 'row', gap: spacing.md, padding: spacing.md }, waitingIcon: { alignItems: 'center', backgroundColor: colors.white, borderColor: colors.primary, borderRadius: radius.pill, borderWidth: 1, height: 44, justifyContent: 'center', width: 44 }, waitingCopy: { flex: 1, gap: 2 }, vehicle: { alignItems: 'center', flexDirection: 'row', gap: spacing.md, padding: spacing.md }, vehiclePlaceholder: { alignItems: 'center', backgroundColor: colors.primarySoft, borderRadius: radius.md, height: 98, justifyContent: 'center', width: 105 }, vehicleCopy: { flex: 1, gap: spacing.xs }, sectionHeading: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between' }, quickActions: { flexDirection: 'row', gap: spacing.xs }, quickAction: { alignItems: 'center', borderColor: colors.primary, borderRadius: radius.sm, borderWidth: 1, flex: 1, gap: spacing.xs, justifyContent: 'center', minHeight: 88, paddingHorizontal: 2 }, quickActionLabel: { textAlign: 'center' }, shiftCard: { alignItems: 'center', backgroundColor: colors.primarySoft, flexDirection: 'row', gap: spacing.md, padding: spacing.md }, shiftCopy: { flex: 1, gap: spacing.xxs }, version: { marginTop: spacing.md, textAlign: 'center' }, pressed: { opacity: 0.8, transform: [{ scale: 0.98 }] }, sheetOverlay: { backgroundColor: colors.overlay, flex: 1, justifyContent: 'flex-end' }, sheet: { backgroundColor: colors.surface, borderTopLeftRadius: radius.xl, borderTopRightRadius: radius.xl, gap: spacing.lg, padding: spacing.xl }, sheetHandle: { alignSelf: 'center', backgroundColor: colors.primary, borderRadius: radius.pill, height: 4, width: 72 }, sheetClose: { alignItems: 'center', borderColor: colors.primary, borderRadius: radius.md, borderWidth: 1, justifyContent: 'center', minHeight: 48 } });
