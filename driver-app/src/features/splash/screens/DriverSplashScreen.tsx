import { SafeAreaView, StyleSheet, View } from 'react-native';
import { DriverBrandMark } from '../../../components/brand/DriverBrandMark';
import { DriverButton } from '../../../components/DriverButton';
import { DriverText } from '../../../components/DriverText';
import { colors, spacing } from '../../../theme';

export function DriverSplashScreen({ onContinue }: { onContinue: () => void }) {
  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.content}>
        <View style={styles.hero}>
          <DriverBrandMark size={110} />
          <View style={styles.brandTitleContainer}>
            <DriverText color={colors.primary} size={34} weight="700">VIRGO</DriverText>
            <DriverText color={colors.primary} size={18} weight="600">Happy Cabbing · Driver</DriverText>
          </View>
          <View style={styles.messageBox}>
            <DriverText color={colors.textPrimary} size={16} weight="600" style={styles.headline}>
              Imphal is changing.
            </DriverText>
            <DriverText color={colors.textSecondary} size={13} style={styles.subtitle}>
              Drive with pride. Change the way you travel in the city.
            </DriverText>
          </View>
        </View>
        <DriverButton label="Get Started" onPress={onContinue} />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { backgroundColor: colors.surface, flex: 1 },
  content: { flex: 1, justifyContent: 'space-between', padding: spacing.xxl },
  hero: { alignItems: 'center', gap: spacing.md, marginTop: '35%' },
  brandTitleContainer: { alignItems: 'center', gap: 2 },
  messageBox: { alignItems: 'center', gap: spacing.xs, marginTop: spacing.md },
  headline: { textAlign: 'center' },
  subtitle: { textAlign: 'center', lineHeight: 18 },
});
