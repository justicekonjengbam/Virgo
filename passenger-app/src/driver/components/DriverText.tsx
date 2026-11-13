import type { PropsWithChildren } from 'react';
import { Text, type StyleProp, type TextStyle } from 'react-native';

import { colors, typography } from '../theme';

type DriverTextProps = PropsWithChildren<{ color?: string; style?: StyleProp<TextStyle>; size?: number; weight?: '400' | '500' | '600' | '700' }>;

/** Poppins text primitive. Use weight 600/700 for actions and hierarchy, as in Passenger. */
export function DriverText({ children, color = colors.textPrimary, size = 14, style, weight = '400' }: DriverTextProps) {
  const family = weight === '700' ? typography.family.bold : weight === '600' ? typography.family.semibold : weight === '500' ? typography.family.medium : typography.family.regular;
  return <Text style={[{ color, fontFamily: family, fontSize: size, lineHeight: Math.round(size * 1.45) }, style]}>{children}</Text>;
}
