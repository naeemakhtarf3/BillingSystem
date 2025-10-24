import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const roomApi = axios.create({
  baseURL: `${API_BASE_URL}/rooms`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token if available
roomApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
roomApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const roomService = {
  // Get all rooms with optional filtering
  getRooms: async (params = {}) => {
    try {
      const response = await roomApi.get('/', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch rooms');
    }
  },

  // Get room by ID
  getRoom: async (roomId) => {
    try {
      const response = await roomApi.get(`/${roomId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch room');
    }
  },

  // Create new room
  createRoom: async (roomData) => {
    try {
      const response = await roomApi.post('/', roomData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create room');
    }
  },

  // Update room
  updateRoom: async (roomId, roomData) => {
    try {
      const response = await roomApi.put(`/${roomId}`, roomData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update room');
    }
  },

  // Update room status
  updateRoomStatus: async (roomId, status) => {
    try {
      const response = await roomApi.patch(`/${roomId}/status`, { status });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update room status');
    }
  },

  // Get available rooms
  getAvailableRooms: async (type = null) => {
    try {
      const params = type ? { type } : {};
      const response = await roomApi.get('/available/list', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch available rooms');
    }
  },

  // Check room availability
  checkRoomAvailability: async (roomId) => {
    try {
      const response = await roomApi.get(`/${roomId}/available`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to check room availability');
    }
  },

  // Filter rooms by type
  getRoomsByType: async (type) => {
    try {
      const response = await roomApi.get('/', { params: { type } });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch rooms by type');
    }
  },

  // Filter rooms by status
  getRoomsByStatus: async (status) => {
    try {
      const response = await roomApi.get('/', { params: { status } });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch rooms by status');
    }
  },

  // Get only available rooms
  getAvailableRoomsOnly: async () => {
    try {
      const response = await roomApi.get('/', { params: { available_only: true } });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch available rooms');
    }
  }
};

export default roomService;
