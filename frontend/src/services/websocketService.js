class WebSocketService {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.listeners = new Map();
  }

  connect(userId = null) {
    if (this.socket && this.connected) {
      return;
    }

    const wsUrl = import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8000/ws';
    
    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      this.connected = true;
      this.reconnectAttempts = 0;
      console.log('WebSocket connected');
      this.emit('connected');
    };

    this.socket.onclose = (event) => {
      this.connected = false;
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.emit('disconnected', event.reason);
      this.handleReconnect();
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket connection error:', error);
      this.emit('error', error);
    };

    // Handle incoming messages
    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);
        
        // Handle different message types
        switch (data.type) {
          case 'room_status_update':
            this.emit('room_status_update', data);
            if (data.status === 'occupied') {
              this.emit('room_occupied', data);
            } else if (data.status === 'available') {
              this.emit('room_available', data);
            } else if (data.status === 'maintenance') {
              this.emit('room_maintenance', data);
            }
            break;
            
          case 'admission_update':
            this.emit('admission_update', data);
            if (data.status === 'discharged') {
              this.emit('admission_discharged', data);
            } else if (data.status === 'active') {
              this.emit('admission_created', data);
            }
            break;
            
          case 'room_availability_update':
            this.emit('room_availability_update', data);
            break;
            
          case 'active_admissions_update':
            this.emit('active_admissions_update', data);
            break;
            
          case 'subscription_confirmed':
            this.emit('subscription_confirmed', data);
            break;
            
          case 'unsubscription_confirmed':
            this.emit('unsubscription_confirmed', data);
            break;
            
          case 'pong':
            this.emit('pong', data);
            break;
            
          default:
            console.log('Unknown message type:', data.type);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.connected = false;
      this.listeners.clear();
    }
  }

  subscribeToRoom(roomId) {
    if (this.socket && this.connected) {
      this.socket.send(JSON.stringify({
        type: 'subscribe_room',
        room_id: roomId
      }));
    }
  }

  unsubscribeFromRoom(roomId) {
    if (this.socket && this.connected) {
      this.socket.send(JSON.stringify({
        type: 'unsubscribe_room',
        room_id: roomId
      }));
    }
  }

  ping() {
    if (this.socket && this.connected) {
      this.socket.send(JSON.stringify({
        type: 'ping',
        timestamp: Date.now()
      }));
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in WebSocket event callback:', error);
        }
      });
    }
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      
      console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
      
      setTimeout(() => {
        if (!this.connected) {
          this.connect();
        }
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
      this.emit('max_reconnect_attempts_reached');
    }
  }

  isConnected() {
    return this.connected && this.socket && this.socket.readyState === WebSocket.OPEN;
  }

  getConnectionState() {
    return this.socket ? this.socket.readyState === WebSocket.OPEN : false;
  }

  // Room status update methods
  onRoomStatusUpdate(callback) {
    this.on('room_status_update', callback);
  }

  onRoomOccupied(callback) {
    this.on('room_occupied', callback);
  }

  onRoomAvailable(callback) {
    this.on('room_available', callback);
  }

  onRoomMaintenance(callback) {
    this.on('room_maintenance', callback);
  }

  onRoomAvailabilityUpdate(callback) {
    this.on('room_availability_update', callback);
  }

  // Admission update methods
  onAdmissionUpdate(callback) {
    this.on('admission_update', callback);
  }

  onActiveAdmissionsUpdate(callback) {
    this.on('active_admissions_update', callback);
  }

  onAdmissionDischarged(callback) {
    this.on('admission_discharged', callback);
  }

  onAdmissionCreated(callback) {
    this.on('admission_created', callback);
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;
