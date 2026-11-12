import type { ReactNode } from 'react';
import { Text, type StyleProp, type TextStyle } from 'react-native';

import { colors, typography, type TypographyVariant } from '../../../theme';

type DsTextProps = {
  children: ReactNode;
  variant?: TypographyVariant;
  color?: string;
  numberOfLines?: number;
  style?: StyleProp<TextStyle>;
};

export function DsText({
  children,
  variant = 'body',
  color = colors.textPrimary,
  numberOfLines,
  style,
}: DsTextProps) {
  return (
    <Text numberOfLines={numberOfLines} style={[typography[variant], { color }, style]}>
      {children}
    </Text>

  );
}
