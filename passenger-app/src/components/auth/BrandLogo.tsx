import { Image, ImageStyle, StyleProp } from 'react-native';

type BrandLogoProps = {
  size: number;
  style?: StyleProp<ImageStyle>;
};

/** Primary brand logo for Virgo – Happy Cabbing (aspect ratio 1.5). */
export function BrandLogo({ size, style }: BrandLogoProps) {
  return (
    <Image
      accessibilityLabel="Virgo – Happy Cabbing logo"
      resizeMode="contain"
      source={require('../../assets/brand/virgo-logo.png')}
      style={[{ height: size, width: size * 1.5 }, style]}
    />
  );
}
