import type { ReactNode } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, View } from 'react-native';

import { colors, radius, shadows, spacing } from '../../../theme';
import { DsText } from './DsText';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'small' | 'medium' | 'large';

type DsButtonProps = {
  label: string;
  onPress: () => void;
  variant?: ButtonVariant;
  size?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  leading?: ReactNode;
  trailing?: ReactNode;
  accessibilityLabel?: string;
};

/** Pressable action atom with consistent variants, loading state, accessibility, and touch sizes. */
export function DsButton({
  label,
  onPress,
  variant = 'primary',
  size = 'large',
  disabled = false,
  loading = false,
  leading,
  trailing,
  accessibilityLabel,
}: DsButtonProps) {
  const inactive = disabled || loading;
  const labelColor = variant === 'primary' || variant === 'danger' ? colors.white : colors.primary;

  return (
    <Pressable
      accessibilityLabel={accessibilityLabel ?? label}
      accessibilityRole="button"
      accessibilityState={{ disabled: inactive, busy: loading }}
      disabled={inactive}
      onPress={onPress}
      style={({ pressed }) => [styles.base, styles[size], styles[variant], pressed && !inactive && styles.pressed, inactive && styles.disabled]}
    >
      {loading ? <ActivityIndicator color={labelColor} size="small" /> : <View style={styles.content}>{leading}<DsText variant="label" color={labelColor}>{label}</DsText>{trailing}</View>}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: { alignItems: 'center', borderRadius: radius.md, justifyContent: 'center', paddingHorizontal: spacing.xl },
  small: { minHeight: 36 }, medium: { minHeight: 44 }, large: { minHeight: 52 },
  primary: { ...shadows.card, backgroundColor: colors.primary },
  secondary: { backgroundColor: colors.primarySoft, borderColor: colors.primary, borderWidth: 1 },
  ghost: { backgroundColor: colors.transparent },
  danger: { backgroundColor: colors.error },
  pressed: { opacity: 0.82 }, disabled: { opacity: 0.48 },
  content: { alignItems: 'center', flexDirection: 'row', gap: spacing.sm, justifyContent: 'center' },
});
