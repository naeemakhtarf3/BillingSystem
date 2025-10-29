import api from './api.js';

const patientService = {
  // Get all patients
  getPatients: async () => {
    try {
      const response = await api.get('/patients');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch patients');
    }
  },

  // Get patient by ID
  getPatient: async (patientId) => {
    try {
      const response = await api.get(`/patients/${patientId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch patient');
    }
  },

  // Search patients
  searchPatients: async (query) => {
    try {
      const response = await api.get('/patients', { params: { query } });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to search patients');
    }
  }
};

export default patientService;
