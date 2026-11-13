import type { ReactNode } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, View } from 'react-native';

import { colors, radius, shadows, spacing } from '../theme';
import { DriverText } from './DriverText';

type DriverButtonProps = {
  label: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  leading?: ReactNode;
  disabled?: boolean;
  loading?: boolean;
};

/** Shared high-emphasis action control aligned with the Passenger app button contract. */
export function DriverButton({ label, onPress, variant = 'primary', size = 'large', leading, disabled = false, loading = false }: DriverButtonProps) {
  const inactive = disabled || loading;
  const textColor = variant === 'secondary' ? colors.primary : colors.white;
  return <Pressable accessibilityLabel={label} accessibilityRole="button" accessibilityState={{ busy: loading, disabled: inactive }} disabled={inactive} onPress={onPress} style={({ pressed }) => [styles.button, styles[size], styles[variant], pressed && !inactive && styles.disabled]}>{loading ? <ActivityIndicator color={textColor} size="small"/> : <View style={styles.content}>{leading}<DriverText color={textColor} size={16} weight="700">{label}</DriverText></View>}</Pressable>;
}

const styles = StyleSheet.create({
  button: { alignItems: 'center', borderRadius: radius.md, justifyContent: 'center', paddingHorizontal: spacing.xl },
  small: { minHeight: 36 }, medium: { minHeight: 44 }, large: { minHeight: 56 },
  primary: { ...shadows.card, backgroundColor: colors.primary },
  secondary: { backgroundColor: colors.primarySoft, borderColor: colors.primary, borderWidth: 1 },
  danger: { backgroundColor: colors.error },
  pressed: { opacity: 0.86, transform: [{ scale: 0.99 }] }, disabled: { opacity: 0.48 },
  content: { alignItems: 'center', flexDirection: 'row', gap: spacing.sm, justifyContent: 'center' },
});
