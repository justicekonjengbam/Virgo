import { StyleSheet, View } from 'react-native';
import { BrandLogo } from './BrandLogo';

type BrandMarkProps = { size?: number };

export function BrandMark({ size = 60 }: BrandMarkProps) {
  return (
    <View accessibilityLabel="Virgo – Happy Cabbing" style={[styles.box, { height: size, width: size * 1.5 }]}>
      <BrandLogo size={size} />
    </View>
  );
}

const styles = StyleSheet.create({
  box: {
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
});
