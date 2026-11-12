import AsyncStorage from '@react-native-async-storage/async-storage';

import { environment } from '../../../config/environment';
import { PASSENGER_SESSION_KEY } from '../../../services/apiClient';
import type { RideStatus } from '../data/bookingApi';

type RideStatusListener = (status: RideStatus) => void;
type ConnectionListener = (connected: boolean) => void;
export type DriverLocation = { ride_id: number; latitude: number; longitude: number; heading_degrees: number | null; accuracy_meters: number | null; recorded_at: string };

export function subscribeToRide(
  rideId: number,
  onStatus: RideStatusListener,
  onConnectionChange: ConnectionListener,
  onDriverLocation?: (location: DriverLocation) => void,
): () => void {
  let socket: WebSocket | null = null;
  let retryTimer: ReturnType<typeof setTimeout> | null = null;
  let heartbeat: ReturnType<typeof setInterval> | null = null;
  let stopped = false;
  let retryAttempt = 0;

  const connect = async () => {
    const saved = await AsyncStorage.getItem(PASSENGER_SESSION_KEY);
    if (stopped || !saved) return;
    let accessToken: string | undefined;
    try { accessToken = (JSON.parse(saved) as { access_token?: string }).access_token; }
    catch { return; }
    if (!accessToken) return;

    socket = new WebSocket(
      `${environment.wsBaseUrl}/api/v1/realtime/passengers/rides/${rideId}`,
      undefined,
      { headers: { Authorization: `Bearer ${accessToken}` } },
    );
    socket.onopen = () => {
      retryAttempt = 0;
      onConnectionChange(true);
      heartbeat = setInterval(() => socket?.readyState === WebSocket.OPEN && socket.send('ping'), 20_000);
    };
    socket.onmessage = event => {
      try {
        const message = JSON.parse(event.data) as { type?: string; data?: RideStatus | DriverLocation };
        if (message.type === 'ride.status' && message.data) onStatus(message.data as RideStatus);
        else if (message.type === 'driver.location' && message.data && onDriverLocation) onDriverLocation(message.data as DriverLocation);
      } catch { /* Ignore malformed frames and keep the live connection healthy. */ }
    };
    socket.onerror = () => onConnectionChange(false);
    socket.onclose = () => {
      onConnectionChange(false);
      if (heartbeat) clearInterval(heartbeat);
      if (!stopped) {
        const delay = Math.min(8_000, 500 * 2 ** retryAttempt++);
        retryTimer = setTimeout(() => void connect(), delay);
      }
    };
  };

  void connect();
  return () => {
    stopped = true;
    if (retryTimer) clearTimeout(retryTimer);
    if (heartbeat) clearInterval(heartbeat);
    socket?.close();
  };
}
