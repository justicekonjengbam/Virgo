import { useState, type ReactNode } from 'react';
import { StyleSheet, TextInput, View } from 'react-native';

import { colors, radius, spacing, typography } from '../theme';
import { DriverText } from './DriverText';

type DriverTextFieldProps = {
  label: string;
  value: string;
  onChangeText: (value: string) => void;
  placeholder: string;
  error?: string;
  helperText?: string;
  leading?: ReactNode;
  trailing?: ReactNode;
  editable?: boolean;
  inputMode?: 'numeric' | 'text';
  maxLength?: number;
  autoCapitalize?: 'characters' | 'none' | 'words';
};

/** High-contrast labelled field with focus and error states, shared by all Driver forms. */
export function DriverTextField({ label, value, onChangeText, placeholder, error, helperText, leading, trailing, editable = true, inputMode = 'text', maxLength, autoCapitalize = 'words' }: DriverTextFieldProps) {
  const [focused, setFocused] = useState(false);
  const message = error ?? helperText;
  return <View style={styles.group}><DriverText weight="600">{label}</DriverText><View style={[styles.field, !editable && styles.disabled, focused && styles.focused, error && styles.inputError]}>{leading}<TextInput accessibilityLabel={label} autoCapitalize={inputMode === 'numeric' ? 'none' : autoCapitalize} autoCorrect={false} editable={editable} inputMode={inputMode} keyboardType={inputMode === 'numeric' ? 'number-pad' : 'default'} maxLength={maxLength} onBlur={() => setFocused(false)} onChangeText={onChangeText} onFocus={() => setFocused(true)} placeholder={placeholder} placeholderTextColor={colors.textTertiary} style={styles.input} value={value}/>{trailing}</View>{message ? <DriverText color={error ? colors.error : colors.textSecondary} size={13}>{message}</DriverText> : null}</View>;
}

const styles = StyleSheet.create({ group: { gap: spacing.sm }, field: { alignItems: 'center', backgroundColor: colors.surface, borderColor: colors.primary, borderRadius: radius.md, borderWidth: 1, flexDirection: 'row', gap: spacing.md, minHeight: 56, paddingHorizontal: spacing.lg }, disabled: { backgroundColor: colors.surfaceMuted }, focused: { borderColor: colors.primaryPressed, borderWidth: 2, paddingHorizontal: spacing.md }, input: { ...typography.body, color: colors.textPrimary, flex: 1, paddingVertical: 0 }, inputError: { borderColor: colors.error } });
