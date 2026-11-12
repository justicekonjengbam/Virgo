import { Image, ImageStyle, StyleProp } from 'react-native';

type DriverBrandLogoProps = {
  size: number;
  style?: StyleProp<ImageStyle>;
};

/** Primary brand logo for Virgo Driver – Happy Cabbing (aspect ratio 1.5). */
export function DriverBrandLogo({ size, style }: DriverBrandLogoProps) {
  return (
    <Image
      accessibilityLabel="Virgo – Happy Cabbing logo"
      resizeMode="contain"
      source={require('../../assets/brand/virgo-logo.png')}
      style={[{ height: size, width: size * 1.5 }, style]}
    />
  );
}
