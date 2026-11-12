import { useEffect, useState } from 'react';
import { Linking, Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import {
  DsButton,
  DsCard,
  DsEmptyState,
  DsLoading,
  DsText,
} from '../../../components/design-system';
import { BrandMark } from '../../../components/auth/BrandMark';
import { colors, radius, shadows, spacing } from '../../../theme';
import type { LocationOption } from '../../booking/data/bookingApi';
import { authService } from '../../auth/services/authService';
import { HomeDrawer } from '../components/HomeDrawer';
import type { DrawerDestination } from '../components/HomeDrawer';
import { LocationCard } from '../components/LocationCard';
import { RideOptionCard } from '../components/RideOptionCard';
import type { RecentRide, SavedPlace } from '../domain/homeTypes';
import { usePassengerHome } from '../state/usePassengerHome';
import carImage from '../../../assets/images/car.png';
import bikeImage from '../../../assets/images/bike.png';
import autoImage from '../../../assets/images/auto.png';

type PassengerHomeScreenProps = {
  pickup: LocationOption | null;
  destination: LocationOption | null;
  onLogout: () => void;
  onSelectPickup: () => void;
  onSelectDestination: () => void;
  onEditSavedPlace: (place: SavedPlace) => void;
  onContinueToFare: (categoryId: number) => void;
  onMenuNavigate: (destination: DrawerDestination) => void;
  onBookInstantRide: () => void;
  onBookOutstation: () => void;
  onOpenNotifications: () => void;
  activeRideId?: number | null;
  onResumeRide?: () => void;
};

/** Passenger home - Presentation Ready */
export function PassengerHomeScreen({
  pickup,
  destination,
  onLogout,
  onSelectPickup,
  onSelectDestination,
  onEditSavedPlace,
  onContinueToFare,
  onMenuNavigate,
  onBookInstantRide,
  onBookOutstation,
  onOpenNotifications,
  activeRideId,
  onResumeRide,
}: PassengerHomeScreenProps) {
  const [menuVisible, setMenuVisible] = useState(false);
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
  const { data, error, loading, refresh } = usePassengerHome();

  useEffect(() => {
    if (data?.ride_categories?.length && selectedCategoryId === null) {
      setSelectedCategoryId(data.ride_categories[0].id);
    }
  }, [data, selectedCategoryId]);

  const logout = async () => {
    await authService.clearSession();
    setMenuVisible(false);
    onLogout();
  };

  if (loading)
    return (
      <SafeAreaView style={styles.safeArea}>
        <DsLoading fullScreen label="Loading your ride options…" />
      </SafeAreaView>
    );

  if (error || !data)
    return (
      <SafeAreaView style={styles.safeArea}>
        <DsEmptyState
          actionLabel="Try again"
          description={error ?? 'No Home data is available.'}
          onAction={() => void refresh()}
          title="Unable to load Home"
        />
      </SafeAreaView>
    );

  const selectedCategory = data.ride_categories.find((c) => c.id === selectedCategoryId) ?? data.ride_categories[0];
  const canContinue = !!pickup && !!destination && !!selectedCategoryId;

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* Brand Header */}
        <View style={styles.header}>
          <View style={styles.brandRow}>
            <BrandMark size={38} />
            <View style={styles.brandCopy}>
              <DsText color={colors.primary} variant="h1" style={styles.brandTitle}>
                VIRGO
              </DsText>
              <DsText color={colors.textSecondary} variant="caption" style={styles.brandTagline}>
                Happy Cabbing
              </DsText>
            </View>
          </View>
          <View style={styles.headerActions}>
            <HeaderAction icon="bell-outline" onPress={onOpenNotifications} />
            <HeaderAction icon="menu" onPress={() => setMenuVisible(true)} />
          </View>
        </View>

        {/* Welcoming Greeting */}
        <View style={styles.greetingBanner}>
          <DsText color={colors.textPrimary} variant="h2">
            Where would you like to go?
          </DsText>
          <DsText color={colors.textSecondary} variant="caption">
            Fast, safe, and transparent fares across Imphal
          </DsText>
        </View>

        {/* Pickup & Destination Selector */}
        <LocationCard
          destination={destination}
          onDestinationPress={onSelectDestination}
          onPickupPress={onSelectPickup}
          pickup={pickup}
        />

        {/* Active Ride Resume Banner */}
        {activeRideId ? (
          <Pressable accessibilityRole="button" onPress={onResumeRide}>
            <DsCard elevated style={styles.activeRide}>
              <View style={styles.safetyIcon}>
                <MaterialCommunityIcons color={colors.primary} name="navigation-variant" size={28} />
              </View>
              <View style={styles.safetyCopy}>
                <DsText color={colors.primary} variant="bodyMedium">
                  Continue active ride #{activeRideId}
                </DsText>
                <DsText color={colors.textSecondary} variant="caption">
                  Return to live Driver tracking and ride controls.
                </DsText>
              </View>
              <MaterialCommunityIcons color={colors.primary} name="chevron-right" size={24} />
            </DsCard>
          </Pressable>
        ) : null}

        {/* Saved Places */}
        <SectionTitle action="Manage" onAction={() => onMenuNavigate('addresses')} title="Saved places" />
        <DsCard elevated style={styles.savedPlaces}>
          {['Home', 'Work'].map((label) => (
            <SavedPlaceCard
              key={label}
              onPress={() => {
                const place = data.saved_places.find((item) => item.label === label);
                if (place) onEditSavedPlace(place);
              }}
              place={data.saved_places.find((item) => item.label === label)}
            />
          ))}
        </DsCard>

        {/* Ride Category Cards - All 6 categories */}
        <SectionTitle action="All options" title="Choose a ride" />
        <ScrollView
          contentContainerStyle={styles.rideRowContent}
          horizontal
          showsHorizontalScrollIndicator={false}
        >
          {data.ride_categories.map((category) => (
            <RideOptionCard
              eta={`${category.estimated_arrival_minutes} min away`}
              fare={(category.base_fare_paise / 100).toString()}
              imageSource={vehicleImages[category.code as keyof typeof vehicleImages]}
              key={category.id}
              name={category.display_name}
              onPress={() => setSelectedCategoryId(category.id)}
              selected={selectedCategoryId === category.id}
            />
          ))}
        </ScrollView>

        {/* Fare Preview & Prominent Confirm Ride Button */}
        <DsCard elevated style={styles.fareActionCard}>
          <View style={styles.fareActionRow}>
            <View style={styles.fareActionInfo}>
              <DsText color={colors.textSecondary} variant="caption">Selected category</DsText>
              <DsText color={colors.primary} variant="h2">
                {selectedCategory?.display_name ?? 'Hatchback'}
              </DsText>
              <DsText color={colors.textTertiary} variant="caption">
                Base fare: ₹ {(selectedCategory?.base_fare_paise ?? 8000) / 100} • {selectedCategory?.seat_count ?? 4} seats
              </DsText>
            </View>
            <View style={styles.fareActionBadge}>
              <MaterialCommunityIcons color={colors.primary} name="shield-check" size={20} />
              <DsText color={colors.primary} variant="caption" style={styles.guaranteeText}>
                Best Rate
              </DsText>
            </View>
          </View>
          <DsButton
            label={canContinue ? 'Confirm Ride' : (!destination ? 'Select Destination to Book' : 'Confirm Ride')}
            onPress={() => {
              if (canContinue) {
                onContinueToFare(selectedCategoryId!);
              } else if (!destination) {
                onSelectDestination();
              } else if (!pickup) {
                onSelectPickup();
              }
            }}
            size="large"
          />
        </DsCard>

        {/* Call & Book: +91 6009060341 */}
        <Pressable
          accessibilityHint="Dials Virgo 24x7 phone booking"
          accessibilityLabel="Call and book: +91 6009060341"
          accessibilityRole="button"
          onPress={() => {
            Linking.openURL('tel:+916009060341').catch(() => onBookInstantRide());
          }}
        >
          <DsCard elevated style={styles.callBookCard}>
            <View style={styles.callBookIcon}>
              <MaterialCommunityIcons color={colors.white} name="phone-in-talk" size={26} />
            </View>
            <View style={styles.callBookCopy}>
              <DsText color={colors.primary} variant="h3">
                Call & Book: +91 6009060341
              </DsText>
              <DsText color={colors.textSecondary} variant="caption">
                24x7 phone dispatch • Book a cab instantly
              </DsText>
            </View>
            <MaterialCommunityIcons color={colors.primary} name="chevron-right" size={24} />
          </DsCard>
        </Pressable>

        {/* Outstation Ride Booking */}
        <Pressable
          accessibilityHint="Opens long-distance outstation booking"
          accessibilityLabel="Book outstation ride"
          accessibilityRole="button"
          onPress={onBookOutstation}
        >
          <DsCard elevated style={styles.safetyCard}>
            <View style={styles.safetyIcon}>
              <MaterialCommunityIcons color={colors.primary} name="road-variant" size={28} />
            </View>
            <View style={styles.safetyCopy}>
              <DsText variant="bodyMedium">Outstation ride booking</DsText>
              <DsText color={colors.textTertiary} variant="caption">
                Travel beyond 150 km. Verified drivers & confirmed fares.
              </DsText>
            </View>
            <MaterialCommunityIcons color={colors.primary} name="chevron-right" size={24} />
          </DsCard>
        </Pressable>

        {/* Recent Rides / Booking History */}
        <SectionTitle action="See all" onAction={() => onMenuNavigate('rides')} title="Recent rides" />
        {data.recent_rides.length > 0 ? (
          <View style={styles.recentList}>
            {data.recent_rides.map((ride) => (
              <RecentRide key={ride.id} ride={ride} />
            ))}
          </View>
        ) : (
          <DsCard elevated style={styles.emptyRecentCard}>
            <MaterialCommunityIcons color={colors.primary} name="history" size={26} />
            <View style={styles.emptyRecentCopy}>
              <DsText variant="bodyMedium">No past rides</DsText>
              <DsText color={colors.textTertiary} variant="caption">
                Your completed bookings will be saved here.
              </DsText>
            </View>
          </DsCard>
        )}
      </ScrollView>

      {/* Clean Bottom Navigation Bar */}
      <View style={styles.bottomNav}>
        <Pressable style={styles.navItem} onPress={() => {}}>
          <MaterialCommunityIcons color={colors.primary} name="home" size={24} />
          <DsText color={colors.primary} variant="caption" style={styles.navLabelActive}>
            Home
          </DsText>
        </Pressable>
        <Pressable style={styles.navItem} onPress={() => onMenuNavigate('rides')}>
          <MaterialCommunityIcons color={colors.textSecondary} name="history" size={24} />
          <DsText color={colors.textSecondary} variant="caption">
            My Rides
          </DsText>
        </Pressable>
        <Pressable style={styles.navItem} onPress={onBookOutstation}>
          <MaterialCommunityIcons color={colors.textSecondary} name="road-variant" size={24} />
          <DsText color={colors.textSecondary} variant="caption">
            Outstation
          </DsText>
        </Pressable>
        <Pressable
          style={styles.navItem}
          onPress={() => Linking.openURL('tel:+916009060341').catch(() => onBookInstantRide())}
        >
          <MaterialCommunityIcons color={colors.textSecondary} name="phone" size={24} />
          <DsText color={colors.textSecondary} variant="caption">
            Call & Book
          </DsText>
        </Pressable>
        <Pressable style={styles.navItem} onPress={() => onMenuNavigate('settings')}>
          <MaterialCommunityIcons color={colors.textSecondary} name="account-outline" size={24} />
          <DsText color={colors.textSecondary} variant="caption">
            Account
          </DsText>
        </Pressable>
      </View>

      <HomeDrawer
        activeDestination="home"
        onClose={() => setMenuVisible(false)}
        onLogout={logout}
        onNavigate={(destination) => {
          setMenuVisible(false);
          onMenuNavigate(destination);
        }}
        visible={menuVisible}
      />
    </SafeAreaView>
  );
}

function HeaderAction({ icon, onPress }: { icon: string; onPress?: () => void }) {
  return (
    <Pressable accessibilityLabel={icon} onPress={onPress} style={styles.headerAction}>
      <MaterialCommunityIcons color={colors.primary} name={icon} size={26} />
    </Pressable>
  );
}

const vehicleImages: Record<string, any> = {
  car: carImage,
  hatchback: carImage,
  sedan: carImage,
  suv: carImage,
  bike: bikeImage,
  auto: autoImage,
  e_auto: autoImage,
  e_rickshaw: autoImage,
};

function SavedPlaceCard({ place, onPress }: { place?: SavedPlace; onPress: () => void }) {
  const icon = place?.label === 'Work' ? 'briefcase' : 'home';
  return (
    <Pressable accessibilityRole="button" onPress={onPress} style={styles.savedPlace}>
      <View style={styles.placeIcon}>
        <MaterialCommunityIcons color={colors.primary} name={icon} size={25} />
      </View>
      <View style={styles.savedPlaceCopy}>
        <DsText variant="bodyMedium">{place?.label ?? 'Add place'}</DsText>
        <DsText color={colors.textTertiary} numberOfLines={2} variant="caption">
          {place?.formatted_address ?? 'Choose address'}
        </DsText>
      </View>
      <MaterialCommunityIcons color={colors.primary} name="pencil-outline" size={18} />
    </Pressable>
  );
}

function SectionTitle({ title, action, onAction }: { title: string; action: string; onAction?: () => void }) {
  return (
    <View style={styles.sectionTitle}>
      <DsText variant="h1">{title}</DsText>
      {action ? (
        <Pressable accessibilityRole="button" onPress={onAction}>
          <DsText color={colors.primary}>{action}</DsText>
        </Pressable>
      ) : null}
    </View>
  );
}

function RecentRide({ ride }: { ride: RecentRide }) {
  const [active, setActive] = useState(false);
  const date = ride.completed_at
    ? new Date(ride.completed_at).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      })
    : 'Recently';
  const time = ride.final_duration_seconds
    ? `${Math.round(ride.final_duration_seconds / 60)} min`
    : '—';
  return (
    <Pressable
      accessibilityRole="button"
      onHoverIn={() => setActive(true)}
      onHoverOut={() => setActive(false)}
      onPressIn={() => setActive(true)}
      onPressOut={() => setActive(false)}
      style={[styles.recentPressable, active && styles.recentActive]}
    >
      <DsCard style={styles.recentRide}>
        <View style={styles.routeIcon}>
          <MaterialCommunityIcons color={colors.primary} name="map-marker" size={26} />
        </View>
        <View style={styles.rideInfo}>
          <DsText numberOfLines={1} variant="bodyMedium">
            {ride.pickup_address} → {ride.destination_address}
          </DsText>
          <DsText color={colors.textTertiary}>
            {date} • {time}
          </DsText>
        </View>
        <DsText color={colors.primary} variant="h2">
          ₹ {ride.fare_paise / 100}
        </DsText>
      </DsCard>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  content: {
    backgroundColor: colors.background,
    gap: spacing.lg,
    padding: spacing.lg,
    paddingBottom: spacing.massive * 1.5,
  },
  header: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: spacing.xs,
  },
  brandRow: {
    alignItems: 'center',
    flexDirection: 'row',
    gap: spacing.sm,
  },
  brandCopy: {
    gap: 0,
  },
  brandTitle: {
    fontSize: 22,
    fontWeight: '800',
    letterSpacing: 1,
    lineHeight: 26,
  },
  brandTagline: {
    color: colors.primary,
    fontSize: 12,
    fontWeight: '600',
  },
  headerActions: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  headerAction: {
    ...shadows.card,
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderColor: colors.primary,
    borderRadius: radius.md,
    borderWidth: 1,
    height: 44,
    justifyContent: 'center',
    width: 44,
  },
  greetingBanner: {
    gap: spacing.xxs,
    marginTop: spacing.xs,
  },
  placeIcon: {
    alignItems: 'center',
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
    borderRadius: radius.sm,
    borderWidth: 1,
    height: 48,
    justifyContent: 'center',
    width: 48,
  },
  savedPlace: { alignItems: 'center', flex: 1, flexDirection: 'row', gap: spacing.sm },
  savedPlaceCopy: { flex: 1 },
  savedPlaces: { flexDirection: 'row', gap: spacing.sm, padding: spacing.md },
  rideRowContent: {
    flexDirection: 'row',
    gap: spacing.xs,
    paddingVertical: spacing.xs,
  },
  fareActionCard: {
    borderColor: colors.primary,
    borderRadius: radius.md,
    borderWidth: 1.5,
    gap: spacing.md,
    padding: spacing.md,
  },
  fareActionRow: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  fareActionInfo: {
    flex: 1,
    gap: 2,
  },
  fareActionBadge: {
    alignItems: 'center',
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
    borderRadius: radius.pill,
    borderWidth: 1,
    flexDirection: 'row',
    gap: 4,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
  },
  guaranteeText: {
    color: colors.primary,
    fontWeight: '700',
  },
  callBookCard: {
    alignItems: 'center',
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
    borderRadius: radius.md,
    borderWidth: 1.5,
    flexDirection: 'row',
    gap: spacing.md,
    padding: spacing.md,
  },
  callBookIcon: {
    alignItems: 'center',
    backgroundColor: colors.primary,
    borderRadius: radius.pill,
    height: 48,
    justifyContent: 'center',
    width: 48,
  },
  callBookCopy: {
    flex: 1,
    gap: spacing.xxs,
  },
  safetyCard: { alignItems: 'center', flexDirection: 'row', gap: spacing.md, padding: spacing.md },
  activeRide: {
    alignItems: 'center',
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
    borderWidth: 1,
    flexDirection: 'row',
    gap: spacing.md,
    padding: spacing.md,
  },
  safetyCopy: { flex: 1, gap: spacing.xxs },
  safetyIcon: {
    alignItems: 'center',
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
    borderRadius: radius.sm,
    borderWidth: 1,
    height: 52,
    justifyContent: 'center',
    width: 52,
  },
  sectionTitle: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: -spacing.xs,
  },
  recentList: { gap: spacing.md },
  emptyRecentCard: {
    alignItems: 'center',
    flexDirection: 'row',
    gap: spacing.md,
    padding: spacing.md,
  },
  emptyRecentCopy: {
    flex: 1,
    gap: spacing.xxs,
  },
  recentPressable: { borderRadius: radius.md },
  recentActive: {
    ...shadows.raised,
    borderColor: colors.primary,
    borderRadius: radius.md,
    borderWidth: 1,
    shadowColor: colors.primaryShadow,
    shadowOpacity: 1,
  },
  recentRide: { alignItems: 'center', flexDirection: 'row', gap: spacing.md, padding: spacing.md },
  routeIcon: {
    alignItems: 'center',
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
    borderRadius: radius.sm,
    borderWidth: 1,
    height: 48,
    justifyContent: 'center',
    width: 48,
  },
  rideInfo: { flex: 1, gap: spacing.xxs },
  safeArea: { backgroundColor: colors.background, flex: 1 },
  bottomNav: {
    ...shadows.floating,
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderTopColor: colors.border,
    borderTopWidth: 1,
    bottom: 0,
    flexDirection: 'row',
    height: 64,
    justifyContent: 'space-around',
    left: 0,
    paddingBottom: 4,
    position: 'absolute',
    right: 0,
  },
  navItem: {
    alignItems: 'center',
    gap: 2,
    justifyContent: 'center',
    paddingVertical: 6,
  },
  navLabelActive: {
    color: colors.primary,
    fontWeight: '700',
  },
});
