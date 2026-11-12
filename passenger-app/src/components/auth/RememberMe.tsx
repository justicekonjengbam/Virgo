import { Pressable, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { colors, spacing } from '../../theme';
import { DsText } from '../design-system';

type RememberMeProps = { checked: boolean; onChange: (checked: boolean) => void };

/** Reusable labelled checkbox used by the login and signup flows. */
export function RememberMe({ checked, onChange }: RememberMeProps) {
  return (
    <Pressable accessibilityRole="checkbox" accessibilityState={{ checked }} onPress={() => onChange(!checked)} style={styles.row}>
      <View style={[styles.checkbox, checked && styles.checked]}>
        {checked && <MaterialCommunityIcons color={colors.white} name="check" size={15} />}
      </View>
      <DsText color={colors.textTertiary} style={styles.label}>Remember me</DsText>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  row: { alignItems: 'center', alignSelf: 'flex-start', flexDirection: 'row', gap: spacing.sm },
  checkbox: { alignItems: 'center', borderColor: colors.textTertiary, borderWidth: 1, height: 20, justifyContent: 'center', width: 20 },
  checked: { backgroundColor: colors.primary, borderColor: colors.primary },
  label: { fontSize: 18, lineHeight: 24 },
});
