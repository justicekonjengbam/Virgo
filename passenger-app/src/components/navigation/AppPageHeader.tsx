import { Pressable, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DsText } from '../design-system';
import { colors, radius, shadows, spacing } from '../../theme';

type AppPageHeaderProps = { title: string; onBack: () => void; onMenuPress: () => void };

/** Consistent authenticated-page header: back navigation, centered context, and the app menu. */
export function AppPageHeader({ title, onBack, onMenuPress }: AppPageHeaderProps) {
  return <View style={styles.header}><Pressable accessibilityLabel="Go back" onPress={onBack} style={styles.iconButton}><MaterialCommunityIcons color={colors.primary} name="chevron-left" size={30} /></Pressable><DsText numberOfLines={1} style={styles.title} variant="h2">{title}</DsText><Pressable accessibilityLabel="Open menu" onPress={onMenuPress} style={styles.iconButton}><MaterialCommunityIcons color={colors.primary} name="menu" size={27} /></Pressable></View>;
}

const styles = StyleSheet.create({ header: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between', minHeight: 52 }, iconButton: { ...shadows.card, alignItems: 'center', backgroundColor: colors.surface, borderColor: colors.primary, borderRadius: radius.md, borderWidth: 1, height: 48, justifyContent: 'center', width: 48 }, title: { flex: 1, marginHorizontal: spacing.md, textAlign: 'center' } });
