import type { ReactNode } from 'react';
import { StyleSheet, View, type StyleProp, type ViewStyle } from 'react-native';

import { colors, radius, shadows, spacing } from '../../../theme';

type DsCardProps = { children: ReactNode; elevated?: boolean; style?: StyleProp<ViewStyle> };

/** Surface molecule for grouped content such as ride summaries and selectable options. */
export function DsCard({ children, elevated = false, style }: DsCardProps) {
  return <View style={[styles.card, elevated && shadows.card, style]}>{children}</View>;
}

const styles = StyleSheet.create({ card: { backgroundColor: colors.surface, borderColor: colors.border, borderRadius: radius.lg, borderWidth: 1, padding: spacing.lg } });
