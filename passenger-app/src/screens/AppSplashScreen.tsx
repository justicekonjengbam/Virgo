import { useEffect, useRef } from 'react';
import { Animated, SafeAreaView, StyleSheet, View } from 'react-native';

import { BrandMark } from '../components/auth/BrandMark';
import { DsButton, DsText } from '../components/design-system';
import { colors, radius, shadows, spacing } from '../theme';

type AppSplashScreenProps = {
  onFinish: () => void;
};

/**
 * Startup splash screen featuring the Virgo logo, title, and tagline.
 * Remains visible until the user explicitly taps "Get Started".
 */
export function AppSplashScreen({ onFinish }: AppSplashScreenProps) {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.92)).current;
  const finishedRef = useRef(false);

  const handleFinish = () => {
    if (finishedRef.current) return;
    finishedRef.current = true;
    onFinish();
  };

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 650,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        friction: 6,
        tension: 40,
        useNativeDriver: true,
      }),
    ]).start();
    // Intentionally no auto-advance timer: stays until the user presses "Get Started"
  }, [fadeAnim, scaleAnim]);

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.content}>
        <Animated.View
          style={[
            styles.hero,
            {
              opacity: fadeAnim,
              transform: [{ scale: scaleAnim }],
            },
          ]}
        >
          <View style={styles.logoWrapper}>
            <BrandMark size={120} />
          </View>

          <View style={styles.brandTitleContainer}>
            <DsText color={colors.primary} style={styles.title} variant="display">
              VIRGO
            </DsText>
            <DsText color={colors.primary} style={styles.tagline} variant="h3">
              Happy Cabbing
            </DsText>
          </View>

          <View style={styles.divider} />

          <View style={styles.messageBox}>
            <DsText color={colors.textPrimary} style={styles.headline} variant="bodyMedium">
              Imphal is changing.
            </DsText>
            <DsText color={colors.textSecondary} style={styles.subtitle} variant="caption">
              Change the way you travel in the city.
            </DsText>
          </View>
        </Animated.View>

        <View style={styles.footer}>
          <DsButton
            label="Get Started"
            onPress={handleFinish}
            size="large"
            variant="primary"
          />
          <DsText color={colors.textTertiary} style={styles.versionText} variant="caption">
            Virgo • Happy Cabbing • v1.0.0
          </DsText>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    backgroundColor: colors.surface,
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'space-between',
    paddingHorizontal: spacing.xxl,
    paddingTop: spacing.xxl,
    paddingBottom: spacing.xxl,
  },
  hero: {
    alignItems: 'center',
    gap: spacing.md,
    marginTop: '28%',
  },
  logoWrapper: {
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.xs,
  },
  brandTitleContainer: {
    alignItems: 'center',
    gap: 2,
  },
  title: {
    fontSize: 40,
    fontWeight: '800',
    letterSpacing: 2,
    textAlign: 'center',
  },
  tagline: {
    fontWeight: '600',
    letterSpacing: 1,
    textAlign: 'center',
  },
  divider: {
    backgroundColor: colors.primarySoft,
    borderRadius: radius.pill,
    height: 3,
    marginTop: spacing.xs,
    width: 48,
  },
  messageBox: {
    alignItems: 'center',
    gap: spacing.xs,
    marginTop: spacing.md,
  },
  headline: {
    fontSize: 17,
    fontWeight: '600',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 13,
    lineHeight: 19,
    textAlign: 'center',
  },
  footer: {
    gap: spacing.md,
    width: '100%',
  },
  versionText: {
    textAlign: 'center',
  },
});
