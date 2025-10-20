import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Select, MenuItem, FormControl, InputLabel, Box } from '@mui/material';
import { applyStatusFilter, isEmptyResults } from '../utils/filterUtils';
import { useFilterState } from '../hooks/useFilterState';
import { isStorageAvailable } from '../utils/localStorage';
import { handleStorageError } from '../utils/errorHandling';
import NoResultsMessage from './NoResultsMessage';

/**
 * StatusFilterDropdown Component
 * 
 * A Material-UI based dropdown component for filtering invoices by status.
 * Provides client-side filtering with localStorage persistence and empty state handling.
 * 
 * Features:
 * - Real-time filtering with immediate visual feedback
 * - localStorage persistence across page reloads
 * - Empty state handling with user-friendly messages
 * - Error handling and graceful degradation
 * - Accessibility support with ARIA labels
 * - Performance optimization with useCallback and useMemo
 * 
 * @param {Object} props - Component props
 * @param {Array} props.invoices - Array of invoice objects to filter
 * @param {Function} props.onFilterChange - Callback function when filter changes
 * @param {string} [props.initialFilter='all'] - Initial filter selection
 * @param {boolean} [props.showNoResultsMessage=true] - Whether to show empty state message
 * 
 * @example
 * <StatusFilterDropdown
 *   invoices={invoiceData}
 *   onFilterChange={handleFilterChange}
 *   initialFilter="paid"
 *   showNoResultsMessage={true}
 * />
 */
const StatusFilterDropdown = ({ 
  invoices = [], 
  onFilterChange, 
  initialFilter = 'all',
  showNoResultsMessage = true
}) => {
  // Use the custom hook for state management with localStorage persistence
  const { selectedFilter, updateFilter, isPersisted } = useFilterState(initialFilter);
  const [filteredInvoices, setFilteredInvoices] = useState([]);
  
  // Check localStorage availability on component mount
  useEffect(() => {
    if (!isStorageAvailable()) {
      handleStorageError(
        new Error('localStorage not available'),
        'StatusFilterDropdown: localStorage not available',
        'LOW'
      );
    }
    
    // Development mode logging
    if (process.env.NODE_ENV === 'development') {
      console.log('StatusFilterDropdown: Component mounted', {
        invoicesCount: invoices.length,
        initialFilter,
        showNoResultsMessage
      });
    }
  }, []);

  // Memoize filtered results for performance optimization
  const memoizedFilteredInvoices = useMemo(() => {
    return applyStatusFilter(invoices, selectedFilter);
  }, [invoices, selectedFilter]);

  // Memoize empty state check for performance
  const isEmpty = useMemo(() => {
    return isEmptyResults(memoizedFilteredInvoices);
  }, [memoizedFilteredInvoices]);

  /**
   * Handle filter selection change with immediate application and persistence
   * @param {Event} event - Material-UI Select change event
   */
  const handleFilterChange = useCallback((event) => {
    const newFilter = event.target.value;
    
    // Development mode logging
    if (process.env.NODE_ENV === 'development') {
      console.log('StatusFilterDropdown: Filter change', {
        newFilter,
        previousFilter: selectedFilter,
        invoicesCount: invoices.length,
        timestamp: new Date().toISOString()
      });
    }
    
    try {
      // Update filter state (this will also persist to localStorage)
      updateFilter(newFilter);
      
      // Use memoized filtered results for performance
      setFilteredInvoices(memoizedFilteredInvoices);
      
      // Notify parent component immediately
      if (onFilterChange) {
        onFilterChange(memoizedFilteredInvoices);
      }
    } catch (error) {
      handleStorageError(
        error,
        'StatusFilterDropdown: Failed to update filter state',
        'MEDIUM'
      );
      
      // Fallback: still apply filter even if persistence fails
      setFilteredInvoices(memoizedFilteredInvoices);
      if (onFilterChange) {
        onFilterChange(memoizedFilteredInvoices);
      }
    }
  }, [invoices, onFilterChange, updateFilter, selectedFilter, memoizedFilteredInvoices]);

  // Apply filter when invoices change (for external data updates)
  useEffect(() => {
    setFilteredInvoices(memoizedFilteredInvoices);
    if (onFilterChange) {
      onFilterChange(memoizedFilteredInvoices);
    }
  }, [memoizedFilteredInvoices, onFilterChange]);

  return (
    <Box sx={{ minWidth: 120 }}>
      <FormControl fullWidth>
        <InputLabel id="status-filter-label">Status</InputLabel>
        <Select
          labelId="status-filter-label"
          id="status-filter-select"
          value={selectedFilter}
          label="Status"
          onChange={handleFilterChange}
          aria-label="Filter invoices by status"
          aria-describedby="status-filter-description"
          sx={{
            '& .MuiOutlinedInput-root': {
              '&:hover fieldset': {
                borderColor: '#1976d2',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#1976d2',
              },
            },
            '& .MuiSelect-select': {
              color: '#1976d2',
            },
            '& .MuiInputLabel-root': {
              color: '#1976d2',
              '&.Mui-focused': {
                color: '#1976d2',
              },
            },
          }}
        >
          <MenuItem value="all" aria-label="Show all invoices">All</MenuItem>
          <MenuItem value="paid" aria-label="Show only paid invoices">Paid</MenuItem>
          <MenuItem value="issued" aria-label="Show only issued invoices">Issued</MenuItem>
        </Select>
      </FormControl>
      
      {/* Hidden description for screen readers */}
      <Box 
        id="status-filter-description" 
        sx={{ display: 'none' }}
        aria-hidden="true"
      >
        Select a status to filter invoices. Options include All, Paid, and Issued.
      </Box>
       
      
      {/* No results message */}
      {showNoResultsMessage && isEmpty && (
        <NoResultsMessage 
          filterType={`${selectedFilter} status`}
          message={`No invoices with "${selectedFilter}" status found.`}
        />
      )}
    </Box>
  );
};

export default StatusFilterDropdown;
