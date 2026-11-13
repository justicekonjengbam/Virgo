import 'react-native-gesture-handler';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

import { DsLoading } from './src/components/design-system';
import { AppModeProvider, useAppMode } from './src/context/AppModeContext';
import { DriverNavigator } from './src/driver/navigation/DriverNavigator';
import { PassengerNavigator } from './src/navigation/PassengerNavigator';
import { ModeSelectionScreen } from './src/screens/ModeSelectionScreen';

function AppContent() {
  const { mode, isReady } = useAppMode();

  if (!isReady) {
    return <DsLoading fullScreen label="Loading Virgo…" />;
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
