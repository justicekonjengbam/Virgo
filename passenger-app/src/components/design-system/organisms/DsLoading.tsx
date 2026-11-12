import { ActivityIndicator, StyleSheet, View } from 'react-native';

import { colors, spacing } from '../../../theme';
import { DsText } from '../atoms/DsText';

type DsLoadingProps = { label?: string; fullScreen?: boolean };

/** Loading organism for inline and full-page asynchronous states. */
export function DsLoading({ label = 'Loading…', fullScreen = false }: DsLoadingProps) {
  return <View accessibilityLiveRegion="polite" style={[styles.container, fullScreen && styles.fullScreen]}><ActivityIndicator color={colors.primary} size="small" /><DsText color={colors.textSecondary}>{label}</DsText></View>;
}

const styles = StyleSheet.create({ container: { alignItems: 'center', gap: spacing.md, justifyContent: 'center' }, fullScreen: { flex: 1 } });
