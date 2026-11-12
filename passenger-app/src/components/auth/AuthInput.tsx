import type { ComponentProps } from 'react';
import { StyleSheet, TextInput, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { colors, radius, spacing, typography } from '../../theme';
import { DsText } from '../design-system';

type IconName = ComponentProps<typeof MaterialCommunityIcons>['name'];

type AuthInputProps = {
  icon: IconName;
  label: string;
  placeholder: string;
  trailingLabel?: string;
  prefix?: string;
  maxLength?: number;
  editable?: boolean;
  inputMode?: 'email' | 'numeric' | 'tel' | 'text';
  onChangeText?: (value: string) => void;
  secureTextEntry?: boolean;
  value?: string;
  error?: string;
};

/** Auth-specific input molecule matching the icon, label, outline, and trailing-action pattern in Figma. */
export function AuthInput({
  icon,
  label,
  placeholder,
  trailingLabel,
  prefix,
  maxLength,
  editable = true,
  inputMode = 'text',
  onChangeText,
  secureTextEntry = false,
  value,
  error,
}: AuthInputProps) {
  return (
    <View style={styles.group}>
      <DsText variant="h3" style={styles.label}>{label}</DsText>
      <View style={[styles.field, error && styles.fieldError]}>
        <MaterialCommunityIcons color={colors.textTertiary} name={icon} size={28} />
        {prefix ? <DsText color={colors.textSecondary} variant="body">{prefix}</DsText> : null}
        <TextInput
          accessibilityLabel={label}
          autoCapitalize="none"
          autoCorrect={false}
          inputMode={inputMode}
          keyboardType={inputMode === 'numeric' || inputMode === 'tel' ? 'number-pad' : 'default'}
          editable={editable}
          maxLength={maxLength}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor={colors.textTertiary}
          secureTextEntry={secureTextEntry}
          style={styles.input}
          value={value}
        />
        {trailingLabel && <DsText color={colors.textTertiary} variant="body">{trailingLabel}</DsText>}
      </View>
      {error ? <DsText color={colors.error} variant="caption">{error}</DsText> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  group: { gap: spacing.sm },
  label: { fontFamily: typography.family.regular },
  field: {
    alignItems: 'center',
    borderColor: colors.primary,
    borderRadius: radius.md,
    borderWidth: 1,
    flexDirection: 'row',
    gap: spacing.md,
    minHeight: 56,
    paddingHorizontal: spacing.lg,
  },
  fieldError: { borderColor: colors.error },
  input: { ...typography.body, color: colors.textPrimary, flex: 1, paddingVertical: 0 },
});
