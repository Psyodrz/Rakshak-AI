/**
 * WebSocket Service for RAKSHAK-AI
 * 
 * Module-level singleton that exists OUTSIDE React's lifecycle.
 * This prevents React.StrictMode from disrupting the connection.
 */

const WS_URL = import.meta.env.VITE_WS_URL || (import.meta.env.PROD 
  ? 'wss://rakshak-ai-backend.onrender.com/ws' 
  : 'ws://127.0.0.1:8000/ws');

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.listeners = new Set();
    this.retryCount = 0;
    this.maxRetries = 5;
    this.retryTimeout = null;
    this.initialized = false;
  }

  init() {
    if (this.initialized) return;
    this.initialized = true;
    this.connect();
  }

  connect() {
    if (this.socket?.readyState === WebSocket.OPEN || 
        this.socket?.readyState === WebSocket.CONNECTING) {
      return;
    }

    if (this.retryCount >= this.maxRetries) {
      console.warn('WebSocket: Max retries reached');
      this.notifyListeners();
      return;
    }

    console.log(`WebSocket: Connecting... (attempt ${this.retryCount + 1})`);
    
    try {
      this.socket = new WebSocket(WS_URL);
      
      this.socket.onopen = () => {
        console.log('WebSocket: Connected!');
        this.isConnected = true;
        this.retryCount = 0;
        this.notifyListeners();
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket: Message -', data.type);
          this.notifyListeners(data);
        } catch (e) {
          console.error('WebSocket: Parse error', e);
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket: Error', error);
      };

      this.socket.onclose = (event) => {
        console.log(`WebSocket: Closed (code: ${event.code})`);
        this.isConnected = false;
        this.socket = null;
        this.notifyListeners();

        // Retry with exponential backoff
        if (this.retryCount < this.maxRetries) {
          const delay = 3000 * Math.pow(1.5, this.retryCount);
          console.log(`WebSocket: Retrying in ${Math.round(delay)}ms...`);
          this.retryTimeout = setTimeout(() => {
            this.retryCount++;
            this.connect();
          }, delay);
        }
      };
    } catch (error) {
      console.error('WebSocket: Failed to create', error);
      this.retryCount++;
    }
  }

  subscribe(callback) {
    this.listeners.add(callback);
    // Immediately notify of current state
    callback({ isConnected: this.isConnected, message: null });
    return () => this.listeners.delete(callback);
  }

  notifyListeners(message = null) {
    this.listeners.forEach(callback => {
      callback({ isConnected: this.isConnected, message });
    });
  }

  send(data) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(typeof data === 'string' ? data : JSON.stringify(data));
    }
  }

  getStatus() {
    return {
      isConnected: this.isConnected,
      retryCount: this.retryCount,
      connectionFailed: this.retryCount >= this.maxRetries
    };
  }
}

// Create singleton instance
const wsService = new WebSocketService();

// Auto-initialize when module loads
wsService.init();

export default wsService;
