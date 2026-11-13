import { Pressable, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DriverBrandMark } from './brand/DriverBrandMark';
import { DriverText } from './DriverText';
import { colors, radius, shadows, spacing } from '../theme';

export function DriverPageHeader({ title, onBack }: { title: string; onBack: () => void }) {
  return <View style={styles.header}><Pressable accessibilityLabel="Go back" accessibilityRole="button" onPress={onBack} style={styles.action}><MaterialCommunityIcons color={colors.primary} name="chevron-left" size={30}/></Pressable><View style={styles.title}><DriverBrandMark size={28}/><DriverText color={colors.textPrimary} size={19} weight="700">{title}</DriverText></View><View style={styles.spacer}/></View>;
}

const styles = StyleSheet.create({ header: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between', paddingHorizontal: spacing.xl, paddingVertical: spacing.md }, action: { ...shadows.card, alignItems: 'center', backgroundColor: colors.surface, borderColor: colors.primary, borderRadius: radius.md, borderWidth: 1, height: 48, justifyContent: 'center', width: 48 }, title: { alignItems: 'center', flexDirection: 'row', gap: spacing.sm }, spacer: { width: 48 } });
