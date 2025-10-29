import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { roomService } from '../services/roomApi';
import websocketService from '../services/websocketService';

const RoomContext = createContext();

const initialState = {
  rooms: [],
  availableRooms: [],
  loading: false,
  error: null,
  selectedRoom: null,
  filters: {
    type: null,
    status: null,
    available_only: false
  }
};

const roomReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'SET_ROOMS':
      return { 
        ...state, 
        rooms: action.payload, 
        loading: false, 
        error: null 
      };
    case 'SET_AVAILABLE_ROOMS':
      return { 
        ...state, 
        availableRooms: action.payload, 
        loading: false, 
        error: null 
      };
    case 'ADD_ROOM':
      return { 
        ...state, 
        rooms: [action.payload, ...state.rooms]
      };
    case 'UPDATE_ROOM':
      return {
        ...state,
        rooms: state.rooms.map(room => 
          room.id === action.payload.id ? action.payload : room
        ),
        availableRooms: state.availableRooms.map(room => 
          room.id === action.payload.id ? action.payload : room
        )
      };
    case 'SET_SELECTED_ROOM':
      return { ...state, selectedRoom: action.payload };
    case 'SET_FILTERS':
      return { ...state, filters: { ...state.filters, ...action.payload } };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    case 'ROOM_STATUS_UPDATE':
      return {
        ...state,
        rooms: state.rooms.map(room => 
          room.id === action.payload.room_id ? { ...room, status: action.payload.status } : room
        ),
        availableRooms: state.availableRooms.filter(room => 
          room.id !== action.payload.room_id || action.payload.status === 'available'
        )
      };
    case 'ROOM_AVAILABILITY_UPDATE':
      return {
        ...state,
        rooms: state.rooms.map(room => 
          room.id === action.payload.room_id ? { ...room, status: action.payload.available ? 'available' : 'occupied' } : room
        )
      };
    default:
      return state;
  }
};

export const RoomProvider = ({ children }) => {
  const [state, dispatch] = useReducer(roomReducer, initialState);

  // WebSocket integration
  useEffect(() => {
    // Connect to WebSocket
    websocketService.connect();

    // Set up room status update listeners
    const handleRoomStatusUpdate = (data) => {
      console.log('Room status update received:', data);
      dispatch({ type: 'ROOM_STATUS_UPDATE', payload: data });
    };

    const handleRoomAvailabilityUpdate = (data) => {
      console.log('Room availability update received:', data);
      dispatch({ type: 'ROOM_AVAILABILITY_UPDATE', payload: data });
    };

    // Subscribe to room updates
    websocketService.onRoomStatusUpdate(handleRoomStatusUpdate);
    websocketService.onRoomAvailabilityUpdate(handleRoomAvailabilityUpdate);

    // Cleanup on unmount
    return () => {
      websocketService.off('room_status_update', handleRoomStatusUpdate);
      websocketService.off('room_availability_update', handleRoomAvailabilityUpdate);
    };
  }, []);

  const fetchRooms = useCallback(async (filters = {}) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      // Only update filters if they're different from current filters
      // This prevents unnecessary re-renders
      dispatch({ type: 'SET_FILTERS', payload: filters });
      
      const response = await roomService.getRooms(filters);
      dispatch({ type: 'SET_ROOMS', payload: response.rooms || response });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  }, []);

  const fetchAvailableRooms = async (type = null) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await roomService.getAvailableRooms(type);
      dispatch({ type: 'SET_AVAILABLE_ROOMS', payload: response });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const createRoom = async (roomData) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await roomService.createRoom(roomData);
      dispatch({ type: 'ADD_ROOM', payload: response });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const updateRoom = async (roomId, roomData) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await roomService.updateRoom(roomId, roomData);
      dispatch({ type: 'UPDATE_ROOM', payload: response });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const updateRoomStatus = async (roomId, status) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await roomService.updateRoomStatus(roomId, status);
      dispatch({ type: 'UPDATE_ROOM', payload: response });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const getRoom = async (roomId) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await roomService.getRoom(roomId);
      dispatch({ type: 'SET_SELECTED_ROOM', payload: response });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const checkRoomAvailability = async (roomId) => {
    try {
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await roomService.checkRoomAvailability(roomId);
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const getRoomsByType = async (type) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await roomService.getRoomsByType(type);
      dispatch({ type: 'SET_ROOMS', payload: response.rooms || response });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const getRoomsByStatus = async (status) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await roomService.getRoomsByStatus(status);
      dispatch({ type: 'SET_ROOMS', payload: response.rooms || response });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const selectRoom = (room) => {
    dispatch({ type: 'SET_SELECTED_ROOM', payload: room });
  };

  const setFilters = (filters) => {
    dispatch({ type: 'SET_FILTERS', payload: filters });
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const getRoomStatistics = () => {
    const totalRooms = state.rooms.length;
    const availableRooms = state.rooms.filter(room => room.status === 'available').length;
    const occupiedRooms = state.rooms.filter(room => room.status === 'occupied').length;
    const maintenanceRooms = state.rooms.filter(room => room.status === 'maintenance').length;
    
    return {
      total_rooms: totalRooms,
      available_rooms: availableRooms,
      occupied_rooms: occupiedRooms,
      maintenance_rooms: maintenanceRooms,
      occupancy_rate: totalRooms > 0 ? (occupiedRooms / totalRooms) * 100 : 0
    };
  };

  const value = {
    ...state,
    fetchRooms,
    fetchAvailableRooms,
    createRoom,
    updateRoom,
    updateRoomStatus,
    getRoom,
    checkRoomAvailability,
    getRoomsByType,
    getRoomsByStatus,
    selectRoom,
    setFilters,
    clearError,
    getRoomStatistics
  };

  return (
    <RoomContext.Provider value={value}>
      {children}
    </RoomContext.Provider>
  );
};

export const useRoomContext = () => {
  const context = useContext(RoomContext);
  if (!context) {
    throw new Error('useRoomContext must be used within a RoomProvider');
  }
  return context;
};

export default RoomContext;
