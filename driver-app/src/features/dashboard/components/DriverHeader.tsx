import { Pressable, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { DriverText } from '../../../components/DriverText';
import { colors, radius, shadows, spacing } from '../../../theme';

export function DriverHeader({ fullName, onMenuPress, onRequestPress }: { fullName: string; onMenuPress: () => void; onRequestPress: () => void }) {
  return (
    <View style={styles.header}>
      <View style={styles.identity}>
        <View style={styles.avatar}>
          <MaterialCommunityIcons color={colors.primary} name="steering" size={28} />
        </View>
        <View style={styles.headerTitles}>
          <View style={styles.brandBadge}>
            <DriverText color={colors.primary} size={12} weight="700">VIRGO DRIVER</DriverText>
            <DriverText color={colors.textTertiary} size={11}> • Happy Cabbing</DriverText>
          </View>
          <DriverText color={colors.textPrimary} size={20} weight="700">Welcome, Driver</DriverText>
          <DriverText color={colors.textSecondary} size={13}>You're ready to drive.</DriverText>
        </View>
      </View>
      <View style={styles.actions}>
        <Pressable accessibilityLabel="View ride request" onPress={onRequestPress} style={styles.action}>
          <MaterialCommunityIcons color={colors.primary} name="bell-outline" size={24} />
        </Pressable>
        <Pressable accessibilityLabel="Open menu" onPress={onMenuPress} style={styles.action}>
          <MaterialCommunityIcons color={colors.primary} name="menu" size={26} />
        </Pressable>
      </View>
    </View>
  );
}
const styles = StyleSheet.create({
  header: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between' },
  identity: { alignItems: 'center', flex: 1, flexDirection: 'row', gap: spacing.md },
  headerTitles: { gap: 1 },
  brandBadge: { alignItems: 'center', flexDirection: 'row' },
  actions: { flexDirection: 'row', gap: spacing.xs },
  avatar: { alignItems: 'center', backgroundColor: colors.primarySoft, borderColor: colors.primary, borderRadius: radius.pill, borderWidth: 1, height: 50, justifyContent: 'center', width: 50 },
  action: { ...shadows.card, alignItems: 'center', backgroundColor: colors.white, borderColor: colors.primary, borderRadius: radius.md, borderWidth: 1, height: 44, justifyContent: 'center', width: 44 },
});
