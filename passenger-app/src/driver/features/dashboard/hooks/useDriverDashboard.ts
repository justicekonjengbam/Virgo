import { useCallback, useEffect, useState } from 'react';

import { driverDashboardService, type DriverDashboard } from '../services/driverDashboardService';

export function useDriverDashboard() {
  const [dashboard, setDashboard] = useState<DriverDashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async (manual = false) => {
    if (manual) setIsRefreshing(true);
    else setIsLoading(true);
    try {
      const response = await driverDashboardService.getDashboard();
      setDashboard(response);
      setError(null);
    } catch {
      setError('Unable to refresh your dashboard. Check your connection and try again.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    const initialLoad = setTimeout(() => { void refresh(); }, 0);
    return () => clearTimeout(initialLoad);
  }, [refresh]);

  const updateAvailability = useCallback(async (isOnline: boolean) => {
    const response = await driverDashboardService.updateAvailability(isOnline);
    setDashboard(response);
    return response;
  }, []);

  return { dashboard, error, isLoading, isRefreshing, refresh, updateAvailability };
}
