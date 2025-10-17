import { useState, useEffect, useCallback } from 'react';
import { loadFromStorage, saveToStorage } from '../utils/localStorage';
import { handleStorageError } from '../utils/errorHandling';

/**
 * Custom hook for managing filter state with localStorage persistence
 * 
 * @param {string} initialFilter - Initial filter value
 * @param {string} storageKey - localStorage key for persistence
 * @returns {Object} Filter state and management functions
 */
export const useFilterState = (initialFilter = 'all', storageKey = 'invoiceStatusFilter') => {
  const [selectedFilter, setSelectedFilter] = useState(initialFilter);
  const [isPersisted, setIsPersisted] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(Date.now());

  /**
   * Load filter state from localStorage on component mount
   */
  useEffect(() => {
    try {
      const savedFilter = loadFromStorage(storageKey);
      if (savedFilter && ['all', 'paid', 'issued'].includes(savedFilter)) {
        setSelectedFilter(savedFilter);
        setIsPersisted(true);
        setLastUpdated(Date.now());
      }
    } catch (error) {
      handleStorageError(error, 'Failed to load filter state from localStorage');
      // Fall back to default filter
      setSelectedFilter(initialFilter);
      setIsPersisted(false);
    }
  }, [storageKey, initialFilter]);

  /**
   * Save filter state to localStorage
   */
  const saveFilterState = useCallback((filter) => {
    try {
      saveToStorage(storageKey, filter);
      setIsPersisted(true);
      setLastUpdated(Date.now());
    } catch (error) {
      handleStorageError(error, 'Failed to save filter state to localStorage');
      setIsPersisted(false);
    }
  }, [storageKey]);

  /**
   * Update filter state and persist to localStorage
   * @param {string} newFilter - New filter value
   */
  const updateFilter = useCallback((newFilter) => {
    setSelectedFilter(newFilter);
    saveFilterState(newFilter);
  }, [saveFilterState]);

  /**
   * Reset filter to default value
   */
  const resetFilter = useCallback(() => {
    updateFilter(initialFilter);
  }, [updateFilter, initialFilter]);

  /**
   * Get current filter state
   */
  const getFilterState = useCallback(() => ({
    selectedFilter,
    isPersisted,
    lastUpdated
  }), [selectedFilter, isPersisted, lastUpdated]);

  return {
    selectedFilter,
    isPersisted,
    lastUpdated,
    updateFilter,
    resetFilter,
    getFilterState
  };
};

export default useFilterState;
