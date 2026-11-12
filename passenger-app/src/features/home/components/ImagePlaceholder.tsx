import { Image, StyleSheet, View, type ImageSourcePropType, type StyleProp, type ViewStyle } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { colors, radius, spacing } from '../../../theme';
import { DsText } from '../../../components/design-system';

type ImagePlaceholderProps = { label: string; source?: ImageSourcePropType; style?: StyleProp<ViewStyle> };

/** Reusable bordered reservation for product imagery that will be supplied later. */
export function ImagePlaceholder({ label, source, style }: ImagePlaceholderProps) {
  return (
    <View accessibilityLabel={`${label} image`} style={[styles.container, style]}>
      {source ? <Image accessibilityLabel={label} resizeMode="contain" source={source} style={styles.image} /> : <><MaterialCommunityIcons color={colors.borderStrong} name="image-outline" size={24} /><DsText color={colors.textTertiary} variant="caption">{label}</DsText></>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: 'center', borderColor: colors.borderStrong, borderRadius: radius.md, borderStyle: 'dashed', borderWidth: 1, gap: spacing.xs, justifyContent: 'center', overflow: 'hidden' },
  image: { height: '100%', width: '100%' },
});
