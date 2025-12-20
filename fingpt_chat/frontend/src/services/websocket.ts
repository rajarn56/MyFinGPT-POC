/** WebSocket client for progress updates */
import { WS_BASE_URL } from '../config/api';
import type { ProgressUpdate } from '../types/progress';

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private sessionId: string | null = null;
  private onMessageCallback: ((update: ProgressUpdate) => void) | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private reconnectTimeoutId: NodeJS.Timeout | null = null;

  connect(sessionId: string, onMessage: (update: ProgressUpdate) => void): void {
    if (this.ws?.readyState === WebSocket.OPEN && this.sessionId === sessionId) {
      return; // Already connected
    }

    this.sessionId = sessionId;
    this.onMessageCallback = onMessage;
    this.reconnectAttempts = 0;
    this._connect();
  }

  private _connect(): void {
    if (!this.sessionId) return;

    try {
      const url = `${WS_BASE_URL}/ws/progress/${this.sessionId}`;
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const update: ProgressUpdate = JSON.parse(event.data);
          if (this.onMessageCallback) {
            this.onMessageCallback(update);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket closed');
        this._attemptReconnect();
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      this._attemptReconnect();
    }
  }

  private _attemptReconnect(): void {
    // Cancel any pending reconnection
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }

    // Only reconnect if we have a valid session ID and haven't exceeded max attempts
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.sessionId) {
      this.reconnectAttempts++;
      this.reconnectTimeoutId = setTimeout(() => {
        this.reconnectTimeoutId = null;
        // Double-check sessionId is still valid before reconnecting
        if (this.sessionId) {
          console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
          this._connect();
        } else {
          this.reconnectAttempts = 0;
        }
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      // Reset reconnect attempts if max reached or no session
      this.reconnectAttempts = 0;
    }
  }

  disconnect(): void {
    // Cancel any pending reconnection attempts
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.sessionId = null;
    this.onMessageCallback = null;
    this.reconnectAttempts = 0;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const wsClient = new WebSocketClient();

