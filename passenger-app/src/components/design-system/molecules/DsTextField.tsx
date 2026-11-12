import type { ReactNode } from 'react';
import { StyleSheet, TextInput, View, type TextInputProps } from 'react-native';

import { colors, radius, spacing, typography } from '../../../theme';
import { DsText } from '../atoms/DsText';

type DsTextFieldProps = TextInputProps & { label?: string; helperText?: string; error?: string; leading?: ReactNode; trailing?: ReactNode };

/** Labelled input molecule with a single visual contract for focus, errors, help, and accessories. */
export function DsTextField({ label, helperText, error, leading, trailing, editable = true, style, ...inputProps }: DsTextFieldProps) {
  const message = error ?? helperText;
  return <View style={styles.root}>{label && <DsText variant="label" style={styles.label}>{label}</DsText>}<View style={[styles.field, !!error && styles.fieldError, !editable && styles.fieldDisabled]}>{leading}<TextInput {...inputProps} accessibilityLabel={label} editable={editable} placeholderTextColor={colors.textTertiary} style={[styles.input, style]} />{trailing}</View>{message && <DsText variant="caption" color={error ? colors.error : colors.textSecondary}>{message}</DsText>}</View>;
}

const styles = StyleSheet.create({ root: { gap: spacing.xs }, label: { color: colors.textSecondary }, field: { alignItems: 'center', backgroundColor: colors.surface, borderColor: colors.border, borderRadius: radius.md, borderWidth: 1, flexDirection: 'row', gap: spacing.sm, minHeight: 52, paddingHorizontal: spacing.md }, fieldError: { borderColor: colors.error }, fieldDisabled: { backgroundColor: colors.surfaceMuted }, input: { ...typography.body, color: colors.textPrimary, flex: 1, paddingVertical: 0 } });
