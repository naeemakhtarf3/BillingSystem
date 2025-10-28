import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const admissionApi = axios.create({
  baseURL: `${API_BASE_URL}/admissions`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token if available
admissionApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
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
admissionApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const admissionService = {
  // Get all admissions with optional filtering
  getAdmissions: async (params = {}) => {
    try {
      const response = await admissionApi.get('/', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch admissions');
    }
  },

  // Get admission by ID
  getAdmission: async (admissionId) => {
    try {
      const response = await admissionApi.get(`/${admissionId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch admission');
    }
  },

  // Create new admission
  createAdmission: async (admissionData) => {
    try {
      // Validate admission data before sending
      if (!admissionData.patient_id || !admissionData.room_id || !admissionData.staff_id) {
        throw new Error('Missing required fields: patient_id, room_id, and staff_id are required');
      }
      
      if (admissionData.patient_id <= 0 || admissionData.room_id <= 0 || admissionData.staff_id <= 0) {
        throw new Error('Invalid IDs: patient_id, room_id, and staff_id must be positive integers');
      }
      
      if (!admissionData.admission_date) {
        throw new Error('Admission date is required');
      }
      
      // Validate admission date
      const admissionDate = new Date(admissionData.admission_date);
      const now = new Date();
      if (admissionDate < now) {
        throw new Error('Admission date cannot be in the past');
      }
      
      const response = await admissionApi.post('/', admissionData);
      return response.data;
    } catch (error) {
      // Enhanced error handling
      if (error.response?.status === 400) {
        const errorDetail = error.response?.data?.detail || error.response?.data?.message;
        throw new Error(errorDetail || 'Invalid admission data');
      } else if (error.response?.status === 409) {
        throw new Error('Room is no longer available or patient is already admitted');
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to create admissions');
      } else if (error.response?.status === 422) {
        const validationErrors = error.response?.data?.detail?.validation_errors || [];
        const errorMessages = validationErrors.map(err => `${err.field}: ${err.message}`).join(', ');
        throw new Error(`Validation failed: ${errorMessages}`);
      } else {
        throw new Error(error.response?.data?.detail || error.message || 'Failed to create admission');
      }
    }
  },

  // Update admission
  updateAdmission: async (admissionId, admissionData) => {
    try {
      const response = await admissionApi.put(`/${admissionId}`, admissionData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update admission');
    }
  },

  // Discharge patient
  dischargePatient: async (admissionId, dischargeData) => {
    try {
      const response = await admissionApi.post(`/${admissionId}/discharge`, dischargeData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to discharge patient');
    }
  },

  // Get active admissions
  getActiveAdmissions: async (params = {}) => {
    try {
      const response = await admissionApi.get('/active/list', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch active admissions');
    }
  },

  // Get admissions for a specific patient
  getPatientAdmissions: async (patientId, params = {}) => {
    try {
      const response = await admissionApi.get(`/patient/${patientId}`, { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch patient admissions');
    }
  },

  // Get admissions for a specific room
  getRoomAdmissions: async (roomId, params = {}) => {
    try {
      const response = await admissionApi.get(`/room/${roomId}`, { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch room admissions');
    }
  },

  // Get admissions by status
  getAdmissionsByStatus: async (status, params = {}) => {
    try {
      const response = await admissionApi.get('/', { 
        params: { status, ...params } 
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch admissions by status');
    }
  },

  // Get only active admissions
  getActiveAdmissionsOnly: async (params = {}) => {
    try {
      const response = await admissionApi.get('/', { 
        params: { active_only: true, ...params } 
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch active admissions');
    }
  },

  // Get discharged admissions
  getDischargedAdmissions: async (params = {}) => {
    try {
      const response = await admissionApi.get('/', { 
        params: { status: 'discharged', ...params } 
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch discharged admissions');
    }
  },

  // Get admission statistics
  getAdmissionStatistics: async () => {
    try {
      const response = await admissionApi.get('/active/statistics');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch admission statistics');
    }
  }
};

export default admissionService;
