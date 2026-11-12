import { Pressable, StyleSheet } from 'react-native';

import { colors, radius, spacing } from '../../../theme';
import { DsText } from '../atoms/DsText';

type ChipTone = 'neutral' | 'primary' | 'success' | 'warning' | 'error';
type DsChipProps = { label: string; selected?: boolean; tone?: ChipTone; onPress?: () => void };

/** Compact status/filter molecule; it can be static or interactive without changing its API. */
export function DsChip({ label, selected = false, tone = 'neutral', onPress }: DsChipProps) {
  const palette = selected ? selectedPalette : palettes[tone];
  return <Pressable accessibilityRole={onPress ? 'button' : 'text'} disabled={!onPress} onPress={onPress} style={[styles.base, { backgroundColor: palette.background }]}><DsText variant="caption" color={palette.text}>{label}</DsText></Pressable>;
}

const palettes = {
  neutral: { background: colors.surfaceMuted, text: colors.textSecondary }, primary: { background: colors.primarySoft, text: colors.primary }, success: { background: colors.successSoft, text: colors.success }, warning: { background: colors.warningSoft, text: colors.warning }, error: { background: colors.errorSoft, text: colors.error },
};
const selectedPalette = { background: colors.primary, text: colors.white };
const styles = StyleSheet.create({ base: { alignSelf: 'flex-start', borderRadius: radius.pill, paddingHorizontal: spacing.md, paddingVertical: spacing.xs } });
