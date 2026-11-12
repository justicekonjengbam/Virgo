import { useState } from 'react';
import { Animated, Pressable, StyleSheet, View, type ImageSourcePropType } from 'react-native';
import { DsCard, DsText } from '../../../components/design-system';
import { colors, spacing } from '../../../theme';
import { ImagePlaceholder } from './ImagePlaceholder';
type RideOptionCardProps = {
  name: string;
  eta: string;
  fare: string;
  imageSource?: ImageSourcePropType;
  selected?: boolean;
  onPress?: () => void;
};

export function RideOptionCard({
  name,
  eta,
  fare,
  imageSource,
  selected = false,
  onPress,
}: RideOptionCardProps) {
  const [lift] = useState(() => new Animated.Value(0));
  const animate = (value: number) =>
    Animated.spring(lift, {
      toValue: value,
      useNativeDriver: true,
      speed: 28,
      bounciness: 2,
    }).start();
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      onPressIn={() => animate(1)}
      onPressOut={() => animate(0)}
      style={styles.pressable}
    >
      <Animated.View
        style={[
          styles.animated,
          {
            transform: [
              { translateY: lift.interpolate({ inputRange: [0, 1], outputRange: [0, -4] }) },
            ],
          },
        ]}
      >
        <DsCard
          elevated
          style={[styles.card, selected && styles.selected, styles.interactionShadow]}
        >
          <ImagePlaceholder label={`${name} image`} source={imageSource} style={styles.image} />
          <View style={styles.details}>
            <DsText numberOfLines={1} variant="h3">{name}</DsText>
            <DsText color={colors.textTertiary} variant="caption">
              {eta}
            </DsText>
            <DsText color={selected ? colors.primary : colors.textPrimary} variant="bodyMedium">
              ₹ {fare}
            </DsText>
          </View>
        </DsCard>
      </Animated.View>
    </Pressable>
  );
}
const styles = StyleSheet.create({
  animated: { width: 122 },
  card: { gap: spacing.xs, minHeight: 140, padding: spacing.sm, width: 122 },
  details: { alignItems: 'center', gap: spacing.xxs },
  image: { height: 56, width: '100%' },
  interactionShadow: { shadowColor: colors.primaryShadow, shadowOpacity: 1, shadowRadius: 10 },
  pressable: { marginRight: spacing.sm },
  selected: { backgroundColor: colors.primarySoft, borderColor: colors.primary, borderWidth: 2 },
});
