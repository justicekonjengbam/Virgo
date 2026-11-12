import { SafeAreaView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DsCard, DsText } from '../../../components/design-system';
import { AppPageHeader } from '../../../components/navigation/AppPageHeader';
import { colors, spacing } from '../../../theme';

type MenuPlaceholderScreenProps = {
  title: string;
  description: string;
  icon: string;
  onBack: () => void;
  onMenuPress: () => void;
};
/** Stable destination shell for menu routes while each complete feature is built. */
export function MenuPlaceholderScreen({
  title,
  description,
  icon,
  onBack,
  onMenuPress,
}: MenuPlaceholderScreenProps) {
  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.content}>
        <AppPageHeader onBack={onBack} onMenuPress={onMenuPress} title={title} />
        <DsCard elevated style={styles.card}>
          <MaterialCommunityIcons color={colors.primary} name={icon} size={40} />
          <DsText variant="h2">Coming next</DsText>
          <DsText color={colors.textSecondary}>{description}</DsText>
        </DsCard>
      </View>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  safe: { backgroundColor: colors.background, flex: 1 },
  content: { gap: spacing.xl, padding: spacing.xl },
  card: { alignItems: 'center', gap: spacing.md, padding: spacing.xxl },
});
