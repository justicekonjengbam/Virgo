import { useCallback, useEffect, useState } from 'react';

import { ApiError } from '../../../services/apiClient';
import { homeApi } from '../data/homeApi';
import type { PassengerHome } from '../domain/homeTypes';

export function usePassengerHome() {
  const [data, setData] = useState<PassengerHome | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const refresh = useCallback(async () => {
    setLoading(true); setError(null);
    try { setData(await homeApi.getHome()); }
    catch (reason) { setError(reason instanceof ApiError ? reason.message : 'Unable to load your home screen.'); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => {
    const task = setTimeout(() => { void refresh(); }, 0);
    return () => clearTimeout(task);
  }, [refresh]);
  return { data, error, loading, refresh };
}
