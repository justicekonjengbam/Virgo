import { useEffect, useRef } from 'react';
import { Animated, Pressable, SafeAreaView, StyleSheet, View } from 'react-native';

import { BrandMark } from '../components/auth/BrandMark';
import { DsButton, DsText } from '../components/design-system';
import { colors, spacing } from '../theme';

type AppSplashScreenProps = {
  onFinish: () => void;
};

/** Root splash screen displaying the brand logo and message on app startup. */
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
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        friction: 6,
        useNativeDriver: true,
      }),
    ]).start();

    // Auto-advance after 2 seconds so user doesn't have to wait or tap if they prefer
    const timer = setTimeout(() => {
      handleFinish();
    }, 2200);

    return () => clearTimeout(timer);
  }, [fadeAnim, scaleAnim]);

  return (
    <SafeAreaView style={styles.safeArea}>
      <Pressable onPress={handleFinish} style={styles.content}>
        <Animated.View
          style={[
            styles.hero,
            {
              opacity: fadeAnim,
              transform: [{ scale: scaleAnim }],
            },
          ]}
        >
          <BrandMark size={115} />
          <View style={styles.brandTitleContainer}>
            <DsText color={colors.primary} style={styles.title} variant="display">
              VIRGO
            </DsText>
            <DsText color={colors.primary} style={styles.tagline} variant="h3">
              Happy Cabbing
            </DsText>
          </View>
          <View style={styles.messageBox}>
            <DsText color={colors.textPrimary} style={styles.headline} variant="bodyMedium">
              Imphal is changing.
            </DsText>
            <DsText color={colors.textSecondary} style={styles.subtitle} variant="caption">
              Change the way you travel in the city.
            </DsText>
          </View>
        </Animated.View>

        <DsButton label="Get Started" onPress={handleFinish} size="large" />
      </Pressable>
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
    padding: spacing.xxl,
  },
  hero: {
    alignItems: 'center',
    gap: spacing.md,
    marginTop: '32%',
  },
  brandTitleContainer: {
    alignItems: 'center',
    gap: 2,
  },
  title: {
    fontSize: 38,
    fontWeight: '800',
    letterSpacing: 2,
    textAlign: 'center',
  },
  tagline: {
    fontWeight: '600',
    letterSpacing: 1,
    textAlign: 'center',
  },
  messageBox: {
    alignItems: 'center',
    gap: spacing.xs,
    marginTop: spacing.lg,
  },
  headline: {
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 13,
    lineHeight: 18,
    textAlign: 'center',
  },
});

