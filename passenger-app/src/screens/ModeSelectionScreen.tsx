import { SafeAreaView, StyleSheet, TouchableOpacity, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { BrandMark } from '../components/auth/BrandMark';
import { DsCard, DsText } from '../components/design-system';
import { useAppMode } from '../context/AppModeContext';
import { colors, radius, shadows, spacing } from '../theme';

export function ModeSelectionScreen() {
  const { setMode } = useAppMode();

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        {/* Brand Header */}
        <View style={styles.header}>
          <BrandMark />
          <View style={styles.badge}>
            <DsText color={colors.primary} variant="caption">
              ALL-IN-ONE VIRGO
            </DsText>
          </View>
        </View>

        {/* Title */}
        <View style={styles.titleBlock}>
          <DsText variant="h1" style={styles.heading}>
            How will you use Virgo today?
          </DsText>
          <DsText color={colors.textSecondary} variant="body">
            Choose your mode to get started. You can easily switch between riding and driving anytime in your profile.
          </DsText>
        </View>

        {/* Options */}
        <View style={styles.cards}>
          {/* Passenger Option */}
          <TouchableOpacity
            activeOpacity={0.88}
            onPress={() => void setMode('passenger')}
            style={styles.cardTouch}
          >
            <DsCard elevated style={styles.optionCard}>
              <View style={[styles.iconCircle, { backgroundColor: colors.primarySoft }]}>
                <MaterialCommunityIcons color={colors.primary} name="car-clock" size={32} />
              </View>
              <View style={styles.cardText}>
                <DsText variant="h2">Book a Ride</DsText>
                <DsText color={colors.textSecondary} variant="caption">
                  Fast, safe, and transparently priced cabs across Imphal and beyond.
                </DsText>
              </View>
              <MaterialCommunityIcons color={colors.primary} name="chevron-right" size={28} />
            </DsCard>
          </TouchableOpacity>

          {/* Driver Option */}
          <TouchableOpacity
            activeOpacity={0.88}
            onPress={() => void setMode('driver')}
            style={styles.cardTouch}
          >
            <DsCard elevated style={styles.optionCard}>
              <View style={[styles.iconCircle, { backgroundColor: colors.successSoft || '#E8F5E9' }]}>
                <MaterialCommunityIcons color={colors.success} name="steering" size={32} />
              </View>
              <View style={styles.cardText}>
                <DsText variant="h2">Drive & Earn</DsText>
                <DsText color={colors.textSecondary} variant="caption">
                  Accept ride requests, manage your vehicle, and track daily earnings.
                </DsText>
              </View>
              <MaterialCommunityIcons color={colors.primary} name="chevron-right" size={28} />
            </DsCard>
          </TouchableOpacity>
        </View>

        {/* Bottom Info Note */}
        <View style={styles.footer}>
          <MaterialCommunityIcons color={colors.textTertiary} name="information-outline" size={18} />
          <DsText color={colors.textTertiary} variant="caption" style={styles.footerText}>
            You can toggle between Passenger & Driver modes anytime from the side drawer.
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
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.xxl,
    paddingBottom: spacing.xl,
    justifyContent: 'space-between',
  },
  header: {
    alignItems: 'center',
    gap: spacing.sm,
  },
  badge: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
    borderWidth: 1,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
  },
  titleBlock: {
    gap: spacing.sm,
    marginTop: spacing.xl,
  },
  heading: {
    fontSize: 26,
    lineHeight: 32,
  },
  cards: {
    gap: spacing.lg,
    marginVertical: spacing.xl,
  },
  cardTouch: {
    borderRadius: radius.lg,
  },
  optionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    padding: spacing.lg,
    borderRadius: radius.lg,
    borderColor: colors.border,
    borderWidth: 1,
  },
  iconCircle: {
    width: 60,
    height: 60,
    borderRadius: radius.pill,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardText: {
    flex: 1,
    gap: spacing.xs,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.xs,
    paddingHorizontal: spacing.md,
  },
  footerText: {
    textAlign: 'center',
    flex: 1,
  },
});

