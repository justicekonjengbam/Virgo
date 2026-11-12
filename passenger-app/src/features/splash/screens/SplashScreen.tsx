import { SafeAreaView, StyleSheet, View } from 'react-native';

import { BrandMark } from '../../../components/auth/BrandMark';
import { DsButton, DsText } from '../../../components/design-system';
import { colors, spacing } from '../../../theme';

type SplashScreenProps = { onContinue: () => void };

/** First-launch screen showcasing the Virgo – Happy Cabbing brand. */
export function SplashScreen({ onContinue }: SplashScreenProps) {
  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.content}>
        <View style={styles.hero}>
          <BrandMark size={110} />
          <View style={styles.brandTitleContainer}>
            <DsText color={colors.primary} variant="display" style={styles.title}>VIRGO</DsText>
            <DsText color={colors.primary} variant="h3" style={styles.tagline}>Happy Cabbing</DsText>
          </View>
          <View style={styles.messageBox}>
            <DsText color={colors.textPrimary} variant="bodyMedium" style={styles.headline}>
              Imphal is changing.
            </DsText>
            <DsText color={colors.textSecondary} variant="caption" style={styles.subtitle}>
              Change the way you travel in the city.
            </DsText>
          </View>
        </View>
        <DsButton label="Get Started" onPress={onContinue} size="large" />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { backgroundColor: colors.surface, flex: 1 },
  content: { flex: 1, justifyContent: 'space-between', padding: spacing.xxl },
  hero: { alignItems: 'center', gap: spacing.md, marginTop: '35%' },
  brandTitleContainer: { alignItems: 'center', gap: 2 },
  title: { fontSize: 36, letterSpacing: 1.5, textAlign: 'center' },
  tagline: { letterSpacing: 0.8, textAlign: 'center', fontWeight: '600' },
  messageBox: { alignItems: 'center', gap: spacing.xs, marginTop: spacing.lg },
  headline: { textAlign: 'center', fontSize: 16, fontWeight: '600' },
  subtitle: { textAlign: 'center', fontSize: 13, lineHeight: 18 },
});
