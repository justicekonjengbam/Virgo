import { SafeAreaView, StyleSheet, TouchableOpacity, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { BrandMark } from '../components/auth/BrandMark';
import { DsText } from '../components/design-system';
import { useAppMode } from '../context/AppModeContext';
import { colors, radius, shadows, spacing } from '../theme';

interface ModeSelectionScreenProps {
  onBack?: () => void;
}

/**
 * Clean, modern Mode Selection screen.
 * Allows the user to choose between Passenger ("Book a Ride") and Driver ("Drive & Earn").
 */
export function ModeSelectionScreen({ onBack }: ModeSelectionScreenProps) {
  const { setMode } = useAppMode();

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        {/* Top Header */}
        <View style={styles.topBar}>
          {onBack ? (
            <TouchableOpacity
              accessibilityLabel="Back to splash"
              activeOpacity={0.7}
              onPress={onBack}
              style={styles.backButton}
            >
              <MaterialCommunityIcons color={colors.primary} name="chevron-left" size={28} />
            </TouchableOpacity>
          ) : (
            <View style={styles.backButtonPlaceholder} />
          )}

          <BrandMark size={55} />

          <View style={styles.backButtonPlaceholder} />
        </View>

        {/* Title & Introduction */}
        <View style={styles.titleSection}>
          <DsText style={styles.mainTitle} variant="h1">
            How will you use Virgo today?
          </DsText>
          <DsText color={colors.textSecondary} style={styles.subTitle} variant="body">
            Choose your mode to begin. You can switch between riding and driving anytime.
          </DsText>
        </View>

        {/* Selection Cards */}
        <View style={styles.cardsContainer}>
          {/* Passenger Option */}
          <TouchableOpacity
            activeOpacity={0.88}
            onPress={() => void setMode('passenger')}
            style={styles.cardTouch}
          >
            <View style={styles.optionCard}>
              <View style={styles.cardTopRow}>
                <View style={[styles.iconBox, { backgroundColor: colors.primarySoft }]}>
                  <MaterialCommunityIcons color={colors.primary} name="car-hatchback" size={30} />
                </View>
                <View style={styles.roleBadgePassenger}>
                  <DsText color={colors.primary} style={styles.roleBadgeText} variant="caption">
                    RIDER
                  </DsText>
                </View>
              </View>

              <View style={styles.cardBody}>
                <DsText style={styles.cardTitle} variant="h2">
                  Book a Ride
                </DsText>
                <DsText color={colors.textSecondary} style={styles.cardDescription} variant="body">
                  Safe, reliable, and upfront-priced cabs across Imphal and outstation trips.
                </DsText>
              </View>

              <View style={styles.cardFooter}>
                <DsText color={colors.primary} style={styles.actionText} variant="bodyMedium">
                  Continue as Rider
                </DsText>
                <View style={styles.arrowCircle}>
                  <MaterialCommunityIcons color={colors.white} name="arrow-right" size={16} />
                </View>
              </View>
            </View>
          </TouchableOpacity>

          {/* Driver Option */}
          <TouchableOpacity
            activeOpacity={0.88}
            onPress={() => void setMode('driver')}
            style={styles.cardTouch}
          >
            <View style={styles.optionCard}>
              <View style={styles.cardTopRow}>
                <View style={[styles.iconBox, { backgroundColor: colors.successSoft || '#E8F5E9' }]}>
                  <MaterialCommunityIcons color={colors.success} name="steering" size={30} />
                </View>
                <View style={styles.roleBadgeDriver}>
                  <DsText color={colors.success} style={styles.roleBadgeText} variant="caption">
                    PARTNER
                  </DsText>
                </View>
              </View>

              <View style={styles.cardBody}>
                <DsText style={styles.cardTitle} variant="h2">
                  Drive & Earn
                </DsText>
                <DsText color={colors.textSecondary} style={styles.cardDescription} variant="body">
                  Accept nearby ride requests, track earnings daily, and drive on your schedule.
                </DsText>
              </View>

              <View style={styles.cardFooter}>
                <DsText color={colors.success} style={styles.actionText} variant="bodyMedium">
                  Continue as Driver
                </DsText>
                <View style={[styles.arrowCircle, { backgroundColor: colors.success }]}>
                  <MaterialCommunityIcons color={colors.white} name="arrow-right" size={16} />
                </View>
              </View>
            </View>
          </TouchableOpacity>
        </View>

        {/* Bottom Switch Note */}
        <View style={styles.footerNote}>
          <MaterialCommunityIcons
            color={colors.textTertiary}
            name="swap-horizontal-circle-outline"
            size={20}
          />
          <DsText color={colors.textTertiary} style={styles.footerNoteText} variant="caption">
            Switch between Rider & Driver anytime from your side drawer or Settings.
          </DsText>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    backgroundColor: colors.background,
    flex: 1,
  },
  container: {
    flex: 1,
    justifyContent: 'space-between',
    paddingBottom: spacing.xl,
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.lg,
  },
  topBar: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    minHeight: 48,
  },
  backButton: {
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.pill,
    borderWidth: 1,
    height: 40,
    justifyContent: 'center',
    width: 40,
    ...shadows.card,
  },
  backButtonPlaceholder: {
    height: 40,
    width: 40,
  },
  titleSection: {
    gap: spacing.xs,
    marginTop: spacing.md,
  },
  mainTitle: {
    color: colors.textPrimary,
    fontSize: 26,
    fontWeight: '800',
    lineHeight: 33,
  },
  subTitle: {
    fontSize: 14,
    lineHeight: 20,
  },
  cardsContainer: {
    gap: spacing.lg,
    marginVertical: spacing.lg,
  },
  cardTouch: {
    borderRadius: radius.xl,
  },
  optionCard: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.xl,
    borderWidth: 1.5,
    gap: spacing.md,
    padding: spacing.xl,
    ...shadows.raised,
  },
  cardTopRow: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  iconBox: {
    alignItems: 'center',
    borderRadius: radius.lg,
    height: 52,
    justifyContent: 'center',
    width: 52,
  },
  roleBadgePassenger: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primaryLight,
    borderRadius: radius.pill,
    borderWidth: 1,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xxs,
  },
  roleBadgeDriver: {
    backgroundColor: colors.successSoft || '#E8F5E9',
    borderColor: '#C8E6C9',
    borderRadius: radius.pill,
    borderWidth: 1,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xxs,
  },
  roleBadgeText: {
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.8,
  },
  cardBody: {
    gap: spacing.xs,
  },
  cardTitle: {
    color: colors.textPrimary,
    fontSize: 20,
    fontWeight: '700',
  },
  cardDescription: {
    fontSize: 13,
    lineHeight: 19,
  },
  cardFooter: {
    alignItems: 'center',
    borderTopColor: colors.border,
    borderTopWidth: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: spacing.md,
  },
  actionText: {
    fontSize: 14,
    fontWeight: '700',
  },
  arrowCircle: {
    alignItems: 'center',
    backgroundColor: colors.primary,
    borderRadius: radius.pill,
    height: 30,
    justifyContent: 'center',
    width: 30,
  },
  footerNote: {
    alignItems: 'center',
    backgroundColor: colors.surfaceMuted,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    flexDirection: 'row',
    gap: spacing.sm,
    justifyContent: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  footerNoteText: {
    flex: 1,
    fontSize: 12,
    lineHeight: 16,
  },
});
