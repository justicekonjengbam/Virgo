import 'react-native-gesture-handler';

import { GestureHandlerRootView } from 'react-native-gesture-handler';

import { DriverNavigator } from './src/navigation/DriverNavigator';

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <DriverNavigator />
    </GestureHandlerRootView>
  );
}
