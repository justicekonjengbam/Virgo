import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

export type RideRequestStatus = 'idle' | 'pending' | 'accepted' | 'declined';

type DriverSession = {
  isOnline: boolean;
  requestStatus: RideRequestStatus;
  setIsOnline: (value: boolean) => void;
  setRequestStatus: (value: RideRequestStatus) => void;
};

const DriverSessionContext = createContext<DriverSession | null>(null);

export function DriverSessionProvider({ children }: { children: ReactNode }) {
  const [isOnline, setIsOnline] = useState(false);
  const [requestStatus, setRequestStatus] = useState<RideRequestStatus>('idle');
  const value = useMemo(() => ({ isOnline, requestStatus, setIsOnline, setRequestStatus }), [isOnline, requestStatus]);
  return <DriverSessionContext.Provider value={value}>{children}</DriverSessionContext.Provider>;
}

export function useDriverSession() {
  const session = useContext(DriverSessionContext);
  if (!session) throw new Error('Driver session is unavailable.');
  return session;
}
