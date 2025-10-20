/**
 * localStorage utility functions for Invoice Status Filter
 * 
 * Provides safe localStorage operations with error handling and fallbacks
 */

/**
 * Load data from localStorage
 * @param {string} key - localStorage key
 * @returns {string|null} Stored value or null if not found/error
 */
export const loadFromStorage = (key) => {
  try {
    if (typeof window === 'undefined' || !window.localStorage) {
      throw new Error('localStorage not available');
    }
    
    const value = window.localStorage.getItem(key);
    return value;
  } catch (error) {
    console.warn(`Failed to load from localStorage key "${key}":`, error);
    return null;
  }
};

/**
 * Save data to localStorage
 * @param {string} key - localStorage key
 * @param {string} value - Value to store
 * @returns {boolean} Success status
 */
export const saveToStorage = (key, value) => {
  try {
    if (typeof window === 'undefined' || !window.localStorage) {
      throw new Error('localStorage not available');
    }
    
    window.localStorage.setItem(key, value);
    return true;
  } catch (error) {
    console.warn(`Failed to save to localStorage key "${key}":`, error);
    return false;
  }
};

/**
 * Remove data from localStorage
 * @param {string} key - localStorage key
 * @returns {boolean} Success status
 */
export const removeFromStorage = (key) => {
  try {
    if (typeof window === 'undefined' || !window.localStorage) {
      throw new Error('localStorage not available');
    }
    
    window.localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.warn(`Failed to remove from localStorage key "${key}":`, error);
    return false;
  }
};

/**
 * Check if localStorage is available
 * @returns {boolean} Availability status
 */
export const isStorageAvailable = () => {
  try {
    if (typeof window === 'undefined' || !window.localStorage) {
      return false;
    }
    
    // Test localStorage functionality
    const testKey = '__localStorage_test__';
    window.localStorage.setItem(testKey, 'test');
    window.localStorage.removeItem(testKey);
    return true;
  } catch (error) {
    return false;
  }
};

/**
 * Get localStorage usage information
 * @returns {Object} Storage usage stats
 */
export const getStorageInfo = () => {
  try {
    if (!isStorageAvailable()) {
      return { available: false, used: 0, total: 0 };
    }
    
    let used = 0;
    for (let key in window.localStorage) {
      if (window.localStorage.hasOwnProperty(key)) {
        used += window.localStorage[key].length + key.length;
      }
    }
    
    return {
      available: true,
      used: used,
      total: 5 * 1024 * 1024, // 5MB typical limit
      percentage: (used / (5 * 1024 * 1024)) * 100
    };
  } catch (error) {
    return { available: false, used: 0, total: 0 };
  }
};
