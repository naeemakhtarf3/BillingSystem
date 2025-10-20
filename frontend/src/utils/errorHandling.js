/**
 * Error handling utilities for Invoice Status Filter
 * 
 * Provides centralized error handling and logging for the filter component
 */

/**
 * Error types for different failure scenarios
 */
export const ERROR_TYPES = {
  STORAGE_ERROR: 'STORAGE_ERROR',
  FILTER_ERROR: 'FILTER_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  COMPONENT_ERROR: 'COMPONENT_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR'
};

/**
 * Error severity levels
 */
export const ERROR_SEVERITY = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL'
};

/**
 * Handle localStorage errors
 * @param {Error} error - Error object
 * @param {string} context - Error context description
 * @param {string} [severity='LOW'] - Error severity level
 */
export const handleStorageError = (error, context, severity = ERROR_SEVERITY.LOW) => {
  const errorInfo = {
    type: ERROR_TYPES.STORAGE_ERROR,
    severity,
    context,
    message: error.message,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent
  };
  
  // Log error based on severity
  if (severity === ERROR_SEVERITY.CRITICAL) {
    console.error('Critical localStorage error:', errorInfo);
  } else if (severity === ERROR_SEVERITY.HIGH) {
    console.error('High severity localStorage error:', errorInfo);
  } else {
    console.warn('localStorage error:', errorInfo);
  }
  
  return errorInfo;
};

/**
 * Handle filter operation errors
 * @param {Error} error - Error object
 * @param {string} context - Error context description
 * @param {string} [severity='MEDIUM'] - Error severity level
 */
export const handleFilterError = (error, context, severity = ERROR_SEVERITY.MEDIUM) => {
  const errorInfo = {
    type: ERROR_TYPES.FILTER_ERROR,
    severity,
    context,
    message: error.message,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent
  };
  
  console.error('Filter operation error:', errorInfo);
  return errorInfo;
};

/**
 * Handle validation errors
 * @param {Error} error - Error object
 * @param {string} context - Error context description
 * @param {string} [severity='MEDIUM'] - Error severity level
 */
export const handleValidationError = (error, context, severity = ERROR_SEVERITY.MEDIUM) => {
  const errorInfo = {
    type: ERROR_TYPES.VALIDATION_ERROR,
    severity,
    context,
    message: error.message,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent
  };
  
  console.warn('Validation error:', errorInfo);
  return errorInfo;
};

/**
 * Handle component errors
 * @param {Error} error - Error object
 * @param {string} context - Error context description
 * @param {string} [severity='HIGH'] - Error severity level
 */
export const handleComponentError = (error, context, severity = ERROR_SEVERITY.HIGH) => {
  const errorInfo = {
    type: ERROR_TYPES.COMPONENT_ERROR,
    severity,
    context,
    message: error.message,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    stack: error.stack
  };
  
  console.error('Component error:', errorInfo);
  return errorInfo;
};

/**
 * Create error boundary for React components
 * @param {Error} error - Error object
 * @param {Object} errorInfo - Additional error information
 * @returns {Object} Error boundary state
 */
export const createErrorBoundaryState = (error, errorInfo) => {
  return {
    hasError: true,
    error: {
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      componentStack: errorInfo.componentStack
    }
  };
};

/**
 * Check if error is recoverable
 * @param {Error} error - Error object
 * @param {string} type - Error type
 * @returns {boolean} Recoverable status
 */
export const isRecoverableError = (error, type) => {
  switch (type) {
    case ERROR_TYPES.STORAGE_ERROR:
      // localStorage errors are usually recoverable
      return true;
    case ERROR_TYPES.FILTER_ERROR:
      // Filter errors are usually recoverable
      return true;
    case ERROR_TYPES.VALIDATION_ERROR:
      // Validation errors are usually recoverable
      return true;
    case ERROR_TYPES.COMPONENT_ERROR:
      // Component errors may not be recoverable
      return false;
    default:
      return false;
  }
};

/**
 * Get user-friendly error message
 * @param {Error} error - Error object
 * @param {string} type - Error type
 * @returns {string} User-friendly error message
 */
export const getUserFriendlyMessage = (error, type) => {
  switch (type) {
    case ERROR_TYPES.STORAGE_ERROR:
      return 'Unable to save your filter preference. Your selection will not be remembered.';
    case ERROR_TYPES.FILTER_ERROR:
      return 'Unable to filter invoices. Please try again.';
    case ERROR_TYPES.VALIDATION_ERROR:
      return 'Invalid data detected. Some invoices may not be displayed correctly.';
    case ERROR_TYPES.COMPONENT_ERROR:
      return 'An unexpected error occurred. Please refresh the page.';
    default:
      return 'An error occurred. Please try again.';
  }
};

/**
 * Log error to external service (placeholder for future implementation)
 * @param {Object} errorInfo - Error information object
 */
export const logToExternalService = (errorInfo) => {
  // Placeholder for external logging service
  // In production, this would send errors to a logging service like Sentry
  console.log('External logging (placeholder):', errorInfo);
};
