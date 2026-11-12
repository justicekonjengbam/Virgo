declare module 'react-native-vector-icons/MaterialCommunityIcons' {
  import type { ComponentType } from 'react';
  import type { StyleProp, TextStyle } from 'react-native';

  const MaterialCommunityIcons: ComponentType<{
    color?: string;
    name: string;
    size?: number;
    style?: StyleProp<TextStyle>;
  }>;

  export default MaterialCommunityIcons;
}
