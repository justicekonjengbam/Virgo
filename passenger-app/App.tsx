import 'react-native-gesture-handler';
import { useState } from 'react';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

import { AppModeProvider, useAppMode } from './src/context/AppModeContext';
import { DriverNavigator } from './src/driver/navigation/DriverNavigator';
import { PassengerNavigator } from './src/navigation/PassengerNavigator';
import { AppSplashScreen } from './src/screens/AppSplashScreen';
import { ModeSelectionScreen } from './src/screens/ModeSelectionScreen';

function AppContent() {
  const { mode, isReady } = useAppMode();
  const [showSplash, setShowSplash] = useState(true);

  if (!isReady || showSplash) {
    return <AppSplashScreen onFinish={() => setShowSplash(false)} />;
  }

  if (mode === 'passenger') {
    return <PassengerNavigator />;
  }

  if (mode === 'driver') {
    return <DriverNavigator />;
  }

  return <ModeSelectionScreen />;
}

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <AppModeProvider>
        <AppContent />
      </AppModeProvider>
    </GestureHandlerRootView>
  );
}
