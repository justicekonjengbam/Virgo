import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type AppMode = 'passenger' | 'driver';

export interface AppModeContextType {
  mode: AppMode | null;
  isReady: boolean;
  setMode: (mode: AppMode) => Promise<void>;
  clearMode: () => Promise<void>;
  switchToPassenger: () => Promise<void>;
  switchToDriver: () => Promise<void>;
}

const STORAGE_KEY = '@virgo_app_mode';

const AppModeContext = createContext<AppModeContextType | null>(null);

export function AppModeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<AppMode | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    void (async () => {
      try {
        const stored = await AsyncStorage.getItem(STORAGE_KEY);
        if (stored === 'passenger' || stored === 'driver') {
          setModeState(stored);
        }
      } catch {
        // Fallback to null (show mode selection on error)
      } finally {
        setIsReady(true);
      }
    })();
  }, []);

  const setMode = async (newMode: AppMode) => {
    try {
      await AsyncStorage.setItem(STORAGE_KEY, newMode);
      setModeState(newMode);
    } catch {
      setModeState(newMode);
    }
  };

  const clearMode = async () => {
    try {
      await AsyncStorage.removeItem(STORAGE_KEY);
      setModeState(null);
    } catch {
      setModeState(null);
    }
  };

  const switchToPassenger = () => setMode('passenger');
  const switchToDriver = () => setMode('driver');

  return (
    <AppModeContext.Provider
      value={{
        mode,
        isReady,
        setMode,
        clearMode,
        switchToPassenger,
        switchToDriver,
      }}
    >
      {children}
    </AppModeContext.Provider>
  );
}

export function useAppMode(): AppModeContextType {
  const context = useContext(AppModeContext);
  if (!context) {
    throw new Error('useAppMode must be used within an AppModeProvider');
  }
  return context;
}

