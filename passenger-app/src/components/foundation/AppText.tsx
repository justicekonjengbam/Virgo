import type { ReactNode } from 'react';
import type { StyleProp, TextStyle } from 'react-native';

import { DsText } from '../design-system';

type AppTextVariant = 'title' | 'body' | 'caption';

type AppTextProps = {
  children: ReactNode;
  variant?: AppTextVariant;
  style?: StyleProp<TextStyle>;
};

export function AppText({ children, variant = 'body', style }: AppTextProps) {
  const designSystemVariant = variant === 'title' ? 'h1' : variant;
  return <DsText style={style} variant={designSystemVariant}>{children}</DsText>;
}
