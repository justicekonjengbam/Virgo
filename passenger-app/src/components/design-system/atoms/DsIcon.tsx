import { StyleSheet, Text, type StyleProp, type TextStyle } from 'react-native';

import { colors } from '../../../theme';

const glyphs = {
  arrowRight: '→',
  arrowLeft: '←',
  close: '×',
  check: '✓',
  chevronDown: '⌄',
  location: '⌖',
  phone: '⌕',
  search: '⌕',
  plus: '+',
  minus: '−',
} as const;

export type IconName = keyof typeof glyphs;

type DsIconProps = { name: IconName; color?: string; size?: number; style?: StyleProp<TextStyle> };

/** Lightweight token-colored icon primitive. Its semantic names keep callers independent of glyph choice. */
export function DsIcon({ name, color = colors.textPrimary, size = 20, style }: DsIconProps) {
  return <Text style={[styles.base, { color, fontSize: size, lineHeight: size }, style]}>{glyphs[name]}</Text>;
}

const styles = StyleSheet.create({ base: { fontFamily: 'Poppins-Medium', includeFontPadding: false } });
