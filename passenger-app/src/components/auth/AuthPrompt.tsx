import { StyleSheet, View } from 'react-native';

import { colors, spacing } from '../../theme';
import { DsButton, DsText } from '../design-system';

type AuthPromptProps = { actionLabel: string; message: string; onAction?: () => void };

/** Account-switch prompt reused below authentication forms. */
export function AuthPrompt({ actionLabel, message, onAction }: AuthPromptProps) {
  return (
    <View style={styles.row}>
      <DsText color={colors.textTertiary} style={styles.message}>{message}</DsText>
      <DsButton label={actionLabel} onPress={onAction ?? (() => undefined)} size="small" variant="ghost" />
    </View>
  );
}

const styles = StyleSheet.create({
  row: { alignItems: 'center', flexDirection: 'row', justifyContent: 'center', marginTop: spacing.huge },
  message: { fontSize: 18, lineHeight: 26 },
});
