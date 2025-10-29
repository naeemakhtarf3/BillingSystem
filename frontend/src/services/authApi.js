import api from './api.js';

const authService = {
  // Get all staff members
  getStaff: async () => {
    try {
      const response = await api.get('/auth/staff');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch staff');
    }
  },

  // Get current staff info
  getCurrentStaff: async () => {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch current staff');
    }
  }
};

export default authService;
