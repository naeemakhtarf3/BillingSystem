import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { admissionService } from '../services/admissionApi';

const AdmissionContext = createContext();

const initialState = {
  admissions: [],
  activeAdmissions: [],
  loading: false,
  error: null,
  selectedAdmission: null
};

const admissionReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'SET_ADMISSIONS':
      return { 
        ...state, 
        admissions: action.payload, 
        loading: false, 
        error: null 
      };
    case 'SET_ACTIVE_ADMISSIONS':
      return { 
        ...state, 
        activeAdmissions: action.payload, 
        loading: false, 
        error: null 
      };
    case 'ADD_ADMISSION':
      return { 
        ...state, 
        admissions: [action.payload, ...state.admissions],
        activeAdmissions: [action.payload, ...state.activeAdmissions]
      };
    case 'UPDATE_ADMISSION':
      return {
        ...state,
        admissions: state.admissions.map(admission => 
          admission.id === action.payload.id ? action.payload : admission
        ),
        activeAdmissions: state.activeAdmissions.filter(admission => 
          admission.id !== action.payload.id
        )
      };
    case 'SET_SELECTED_ADMISSION':
      return { ...state, selectedAdmission: action.payload };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
};

export const AdmissionProvider = ({ children }) => {
  const [state, dispatch] = useReducer(admissionReducer, initialState);

  const fetchAdmissions = async (filters = {}) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await admissionService.getAdmissions(filters);
      dispatch({ type: 'SET_ADMISSIONS', payload: response.admissions || response });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const fetchActiveAdmissions = async (params = {}) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await admissionService.getActiveAdmissions(params);
      dispatch({ type: 'SET_ACTIVE_ADMISSIONS', payload: response });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const createAdmission = async (admissionData) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await admissionService.createAdmission(admissionData);
      dispatch({ type: 'ADD_ADMISSION', payload: response });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const updateAdmission = async (admissionId, admissionData) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await admissionService.updateAdmission(admissionId, admissionData);
      dispatch({ type: 'UPDATE_ADMISSION', payload: response });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const dischargePatient = async (admissionId, dischargeData) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await admissionService.dischargePatient(admissionId, dischargeData);
      dispatch({ type: 'UPDATE_ADMISSION', payload: response.admission });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const getAdmission = async (admissionId) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await admissionService.getAdmission(admissionId);
      dispatch({ type: 'SET_SELECTED_ADMISSION', payload: response });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const getPatientAdmissions = async (patientId, params = {}) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await admissionService.getPatientAdmissions(patientId, params);
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const getRoomAdmissions = async (roomId, params = {}) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });
      
      const response = await admissionService.getRoomAdmissions(roomId, params);
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const selectAdmission = (admission) => {
    dispatch({ type: 'SET_SELECTED_ADMISSION', payload: admission });
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const value = {
    ...state,
    fetchAdmissions,
    fetchActiveAdmissions,
    createAdmission,
    updateAdmission,
    dischargePatient,
    getAdmission,
    getPatientAdmissions,
    getRoomAdmissions,
    selectAdmission,
    clearError
  };

  return (
    <AdmissionContext.Provider value={value}>
      {children}
    </AdmissionContext.Provider>
  );
};

export const useAdmissionContext = () => {
  const context = useContext(AdmissionContext);
  if (!context) {
    throw new Error('useAdmissionContext must be used within an AdmissionProvider');
  }
  return context;
};

export default AdmissionContext;
