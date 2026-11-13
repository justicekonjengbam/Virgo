import { useEffect, useRef } from 'react';
import {
  Animated,
  NativeModules,
  SafeAreaView,
  StyleSheet,
  View,
} from 'react-native';

import { BrandMark } from '../components/auth/BrandMark';
import { DsButton, DsText } from '../components/design-system';
import { colors, radius, spacing } from '../theme';

type AppSplashScreenProps = {
  onFinish: () => void;
};

/**
 * Cinematic startup splash screen.
 * Orchestrated with an audio swell sound effect:
 * - 0.0s – 1.0s: Audio build-up with expanding ambient glowing aura
 * - 1.0s – 1.6s: Audio peak hit with logo spring bounce & brand title reveal
 * - 1.8s – 3.0s: Audio decay with slogan fade and ready-to-tap "Get Started" button
 */
export function AppSplashScreen({ onFinish }: AppSplashScreenProps) {
  // Animation values
  const auraScale = useRef(new Animated.Value(0.6)).current;
  const auraOpacity = useRef(new Animated.Value(0)).current;

  const logoOpacity = useRef(new Animated.Value(0)).current;
  const logoScale = useRef(new Animated.Value(0.72)).current;
  const logoTranslateY = useRef(new Animated.Value(28)).current;

  const titleOpacity = useRef(new Animated.Value(0)).current;
  const titleTranslateY = useRef(new Animated.Value(20)).current;

  const subtitleOpacity = useRef(new Animated.Value(0)).current;
  const subtitleTranslateY = useRef(new Animated.Value(14)).current;

  const buttonOpacity = useRef(new Animated.Value(0)).current;
  const buttonScale = useRef(new Animated.Value(0.94)).current;

  const finishedRef = useRef(false);

  const handleFinish = () => {
    if (finishedRef.current) return;
    finishedRef.current = true;
    NativeModules.SplashSound?.stop();
    onFinish();
  };

  useEffect(() => {
    // 1. Play whoosh swell audio at 100% volume
    try {
      NativeModules.SplashSound?.play();
    } catch {
      // Audio fallback silent if unavailable
    }

    // 2. Phase 1: Build-up swell (0.0s - 1.0s)
    Animated.parallel([
      // Aura expands gently
      Animated.timing(auraScale, {
        toValue: 1.35,
        duration: 1000,
        useNativeDriver: true,
      }),
      Animated.timing(auraOpacity, {
        toValue: 0.55,
        duration: 900,
        useNativeDriver: true,
      }),
      // Logo rises and scales up
      Animated.timing(logoOpacity, {
        toValue: 1,
        duration: 750,
        useNativeDriver: true,
      }),
      Animated.timing(logoTranslateY, {
        toValue: 0,
        duration: 950,
        useNativeDriver: true,
      }),
      Animated.timing(logoScale, {
        toValue: 0.94,
        duration: 950,
        useNativeDriver: true,
      }),
    ]).start();

    // 3. Phase 2: Peak hit (at 1.0s) - Logo spring pop & Title reveal
    const peakTimer = setTimeout(() => {
      Animated.parallel([
        Animated.spring(logoScale, {
          toValue: 1.0,
          friction: 4.5,
          tension: 70,
          useNativeDriver: true,
        }),
        Animated.timing(auraOpacity, {
          toValue: 0.22,
          duration: 900,
          useNativeDriver: true,
        }),
        Animated.timing(titleOpacity, {
          toValue: 1,
          duration: 550,
          useNativeDriver: true,
        }),
        Animated.spring(titleTranslateY, {
          toValue: 0,
          friction: 6,
          tension: 50,
          useNativeDriver: true,
        }),
      ]).start();
    }, 980);

    // 4. Phase 3: Decay & Slogan (at 1.7s)
    const decayTimer = setTimeout(() => {
      Animated.parallel([
        Animated.timing(subtitleOpacity, {
          toValue: 1,
          duration: 600,
          useNativeDriver: true,
        }),
        Animated.timing(subtitleTranslateY, {
          toValue: 0,
          duration: 600,
          useNativeDriver: true,
        }),
      ]).start();
    }, 1650);

    // 5. Phase 4: Button entrance (at 2.2s)
    const buttonTimer = setTimeout(() => {
      Animated.parallel([
        Animated.timing(buttonOpacity, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.spring(buttonScale, {
          toValue: 1.0,
          friction: 5,
          tension: 50,
          useNativeDriver: true,
        }),
      ]).start();
    }, 2150);

    return () => {
      clearTimeout(peakTimer);
      clearTimeout(decayTimer);
      clearTimeout(buttonTimer);
      try {
        NativeModules.SplashSound?.stop();
      } catch {}
    };
  }, []);

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.content}>
        <View style={styles.hero}>
          {/* Ambient Glowing Aura */}
          <Animated.View
            style={[
              styles.auraCircle,
              {
                opacity: auraOpacity,
                transform: [{ scale: auraScale }],
              },
            ]}
          />

          {/* Logo with Spring Pop */}
          <Animated.View
            style={[
              styles.logoWrapper,
              {
                opacity: logoOpacity,
                transform: [{ scale: logoScale }, { translateY: logoTranslateY }],
              },
            ]}
          >
            <BrandMark size={125} />
          </Animated.View>

          {/* Brand Name & Tagline */}
          <Animated.View
            style={[
              styles.brandTitleContainer,
              {
                opacity: titleOpacity,
                transform: [{ translateY: titleTranslateY }],
              },
            ]}
          >
            <DsText color={colors.primary} style={styles.title} variant="display">
              VIRGO
            </DsText>
            <DsText color={colors.primary} style={styles.tagline} variant="h3">
              Happy Cabbing
            </DsText>
            <View style={styles.divider} />
          </Animated.View>

          {/* Slogan */}
          <Animated.View
            style={[
              styles.messageBox,
              {
                opacity: subtitleOpacity,
                transform: [{ translateY: subtitleTranslateY }],
              },
            ]}
          >
            <DsText color={colors.textPrimary} style={styles.headline} variant="bodyMedium">
              Imphal is changing.
            </DsText>
            <DsText color={colors.textSecondary} style={styles.subtitle} variant="caption">
              Change the way you travel in the city.
            </DsText>
          </Animated.View>
        </View>

        {/* Action Button */}
        <Animated.View
          style={[
            styles.footer,
            {
              opacity: buttonOpacity,
              transform: [{ scale: buttonScale }],
            },
          ]}
        >
          <DsButton
            label="Get Started"
            onPress={handleFinish}
            size="large"
            variant="primary"
          />
          <DsText color={colors.textTertiary} style={styles.versionText} variant="caption">
            Virgo • Happy Cabbing • v1.0.0
          </DsText>
        </Animated.View>
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
    marginTop: '26%',
    position: 'relative',
  },
  auraCircle: {
    backgroundColor: colors.primaryLight,
    borderRadius: 140,
    height: 220,
    position: 'absolute',
    top: -20,
    width: 220,
  },
  logoWrapper: {
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.xs,
    zIndex: 2,
  },
  brandTitleContainer: {
    alignItems: 'center',
    gap: 3,
    zIndex: 2,
  },
  title: {
    fontSize: 42,
    fontWeight: '800',
    letterSpacing: 2.5,
    textAlign: 'center',
  },
  tagline: {
    fontSize: 18,
    fontWeight: '600',
    letterSpacing: 1.2,
    textAlign: 'center',
  },
  divider: {
    backgroundColor: colors.primary,
    borderRadius: radius.pill,
    height: 3,
    marginTop: spacing.sm,
    width: 44,
  },
  messageBox: {
    alignItems: 'center',
    gap: spacing.xs,
    marginTop: spacing.md,
    zIndex: 2,
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
    zIndex: 2,
  },
  versionText: {
    textAlign: 'center',
  },
});
