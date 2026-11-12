import { StyleSheet, View } from 'react-native';
import { DriverBrandLogo } from './DriverBrandLogo';

export function DriverBrandMark({ size = 60 }: { size?: number }) {
  return (
    <View accessibilityLabel="Virgo Driver – Happy Cabbing" style={[styles.box, { height: size, width: size * 1.5 }]}>
      <DriverBrandLogo size={size} />
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
