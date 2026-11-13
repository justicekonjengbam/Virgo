import AsyncStorage from '@react-native-async-storage/async-storage';

import { environment } from '../../../config/environment';
import { DRIVER_SESSION_KEY } from '../../../services/apiClient';
import type { DriverRideOffer } from './rideMatchingService';

export type DriverRealtimeEvent =
  | { type: 'ride.offer'; data: DriverRideOffer }
  | { type: 'ride.offer_cleared'; data: { ride_id: number } | null }
  | { type: 'ride.cancelled' | 'ride.driver_arrived' | 'ride.in_progress' | 'ride.completed'; data: { ride_id: number; status: string } }
  | { type: 'outstation.assigned'; data: { booking_id: number; scheduled_at: string } }
  | { type: 'outstation.updated'; data: { booking_id: number; status: string } };

type Listener = (event: DriverRealtimeEvent) => void;
type ConnectionListener = (connected: boolean) => void;

class DriverRealtimeService {
  private socket: WebSocket | null = null;
  private retryTimer: ReturnType<typeof setTimeout> | null = null;
  private heartbeat: ReturnType<typeof setInterval> | null = null;
  private retryAttempt = 0;
  private listeners = new Set<Listener>();
  private connectionListeners = new Set<ConnectionListener>();
  private manuallyStopped = false;

  subscribe(listener: Listener, onConnectionChange?: ConnectionListener): () => void {
    this.listeners.add(listener);
    if (onConnectionChange) this.connectionListeners.add(onConnectionChange);
    this.manuallyStopped = false;
    void this.connect();
    return () => {
      this.listeners.delete(listener);
      if (onConnectionChange) this.connectionListeners.delete(onConnectionChange);
      if (!this.listeners.size) this.stop();
    };
  }

  private async connect(): Promise<void> {
    if (this.socket || this.manuallyStopped) return;
    const saved = await AsyncStorage.getItem(DRIVER_SESSION_KEY);
    if (!saved) return;
    let accessToken: string | undefined;
    try { accessToken = (JSON.parse(saved) as { access_token?: string }).access_token; }
    catch { return; }
    if (!accessToken || this.socket) return;

    this.socket = new WebSocket(
      `${environment.wsBaseUrl}/api/v1/realtime/drivers/me`,
      undefined,
      { headers: { Authorization: `Bearer ${accessToken}` } },
    );
    this.socket.onopen = () => {
      this.retryAttempt = 0;
      this.emitConnection(true);
      this.heartbeat = setInterval(() => this.socket?.readyState === WebSocket.OPEN && this.socket.send('ping'), 20_000);
    };
    this.socket.onmessage = event => {
      try {
        const message = JSON.parse(event.data) as DriverRealtimeEvent;
        if (message.type === 'ride.offer' || message.type === 'ride.offer_cleared' || message.type.startsWith('ride.') || message.type.startsWith('outstation.')) {
          this.listeners.forEach(listener => listener(message));
        }
      } catch { /* A malformed frame must not interrupt future ride offers. */ }
    };
    this.socket.onerror = () => this.emitConnection(false);
    this.socket.onclose = () => {
      this.socket = null;
      this.emitConnection(false);
      if (this.heartbeat) clearInterval(this.heartbeat);
      if (!this.manuallyStopped && this.listeners.size) {
        const delay = Math.min(8_000, 500 * 2 ** this.retryAttempt++);
        this.retryTimer = setTimeout(() => void this.connect(), delay);
      }
    };
  }

  private emitConnection(connected: boolean): void {
    this.connectionListeners.forEach(listener => listener(connected));
  }

  private stop(): void {
    this.manuallyStopped = true;
    if (this.retryTimer) clearTimeout(this.retryTimer);
    if (this.heartbeat) clearInterval(this.heartbeat);
    this.socket?.close();
    this.socket = null;
  }
}

export const driverRealtimeService = new DriverRealtimeService();
