import { useEffect, useState } from 'react';
import { LocationManager, type GeolocationPosition } from '@maplibre/maplibre-react-native';

import { rideMatchingService } from '../../rides/services/rideMatchingService';

export function useDriverLocationReporter(enabled: boolean) {
  const [permissionDenied, setPermissionDenied] = useState(false);
  useEffect(() => {
    if (!enabled) return;
    let active = true;
    let lastSentAt = 0;
    const report = (position: GeolocationPosition) => {
      if (!active || Date.now() - lastSentAt < 5_000) return;
      lastSentAt = Date.now();
      void rideMatchingService.updateLocation(position).catch(() => undefined);
    };
    void LocationManager.requestPermissions().then(granted => {
      if (!active) return;
      setPermissionDenied(!granted);
      if (!granted) return;
      LocationManager.setMinDisplacement(10);
      LocationManager.addListener(report);
      void LocationManager.getCurrentPosition().then(position => position && report(position));
    });
    return () => { active = false; LocationManager.removeListener(report); };
  }, [enabled]);
  return { permissionDenied };
}
