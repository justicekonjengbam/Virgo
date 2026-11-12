import { Pressable, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { colors, radius, shadows } from '../../theme';
import { BrandMark } from './BrandMark';

type AuthHeaderProps = {
  onBack?: () => void;
  onHelp?: () => void;
};

/** Responsive top bar shared by the login, signup, and document-verification flows. */
export function AuthHeader({ onBack, onHelp }: AuthHeaderProps) {
  return (
    <View style={styles.header}>
      <Pressable accessibilityLabel="Go back" hitSlop={8} onPress={onBack} style={styles.iconButton}>
        <MaterialCommunityIcons color={colors.primary} name="chevron-left" size={32} />
      </Pressable>
      <BrandMark />
      <Pressable accessibilityLabel="Get help" hitSlop={8} onPress={onHelp} style={styles.iconButton}>
        <MaterialCommunityIcons color={colors.primary} name="help-circle" size={28} />
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    alignItems: 'center',
    borderBottomColor: colors.primary,
    borderBottomWidth: 1,
    flexDirection: 'row',
    height: 108,
    justifyContent: 'space-between',
    paddingHorizontal: 20,
  },
  iconButton: {
    ...shadows.card,
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderColor: colors.primary,
    borderRadius: radius.md,
    borderWidth: 1,
    height: 48,
    justifyContent: 'center',
    width: 48,
  },
});
