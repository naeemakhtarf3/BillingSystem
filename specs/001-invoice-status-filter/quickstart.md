# Quickstart: Invoice Status Filter

**Feature**: Invoice Status Filter  
**Date**: 2024-01-15  
**Phase**: 1 - Design & Contracts

## Overview

This feature adds a status filter dropdown to the invoices management screen, allowing staff to filter invoices by status (All, Paid, Issued) with client-side filtering and localStorage persistence.

## Quick Implementation Guide

### 1. Component Creation

Create the StatusFilterDropdown component in `frontend/src/components/StatusFilterDropdown.jsx`:

```jsx
import React, { useState, useEffect } from 'react';
import { Select, MenuItem, FormControl, InputLabel } from '@mui/material';

const StatusFilterDropdown = ({ invoices, onFilterChange, initialFilter = 'all' }) => {
  const [selectedFilter, setSelectedFilter] = useState(initialFilter);

  // Load filter state from localStorage on mount
  useEffect(() => {
    const savedFilter = localStorage.getItem('invoiceStatusFilter');
    if (savedFilter) {
      setSelectedFilter(savedFilter);
    }
  }, []);

  // Apply filter when selection changes
  useEffect(() => {
    const filteredInvoices = applyFilter(invoices, selectedFilter);
    onFilterChange(filteredInvoices);
    localStorage.setItem('invoiceStatusFilter', selectedFilter);
  }, [selectedFilter, invoices, onFilterChange]);

  const handleFilterChange = (event) => {
    setSelectedFilter(event.target.value);
  };

  const applyFilter = (invoices, filter) => {
    if (filter === 'all') {
      return invoices;
    }
    return invoices.filter(invoice => invoice.status === filter);
  };

  return (
    <FormControl sx={{ minWidth: 120 }}>
      <InputLabel>Status</InputLabel>
      <Select
        value={selectedFilter}
        onChange={handleFilterChange}
        label="Status"
      >
        <MenuItem value="all">All</MenuItem>
        <MenuItem value="paid">Paid</MenuItem>
        <MenuItem value="issued">Issued</MenuItem>
      </Select>
    </FormControl>
  );
};

export default StatusFilterDropdown;
```

### 2. Integration with Invoice Table

Update the invoices management page to include the filter:

```jsx
import StatusFilterDropdown from '../components/StatusFilterDropdown';

const InvoicesPage = () => {
  const [invoices, setInvoices] = useState([]);
  const [filteredInvoices, setFilteredInvoices] = useState([]);

  // Load invoices from API
  useEffect(() => {
    // Load invoices from /api/v1/invoices
    // setInvoices(apiResponse.invoices);
  }, []);

  const handleFilterChange = (filtered) => {
    setFilteredInvoices(filtered);
  };

  return (
    <div>
      <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
        <StatusFilterDropdown
          invoices={invoices}
          onFilterChange={handleFilterChange}
        />
        <Button variant="contained">Create Invoice</Button>
      </div>
      
      <InvoiceTable invoices={filteredInvoices} />
    </div>
  );
};
```

### 3. Error Handling

Add error handling for localStorage issues:

```jsx
const loadFromStorage = () => {
  try {
    const savedFilter = localStorage.getItem('invoiceStatusFilter');
    if (savedFilter && ['all', 'paid', 'issued'].includes(savedFilter)) {
      return savedFilter;
    }
  } catch (error) {
    console.warn('localStorage not available:', error);
  }
  return 'all';
};
```

## Usage Examples

### Basic Usage
1. Navigate to invoices management screen
2. Select filter from dropdown (All, Paid, Issued)
3. Table updates immediately with filtered results
4. Filter selection persists across page reloads

### Filter Options
- **All**: Shows all invoices regardless of status
- **Paid**: Shows only invoices with status "paid"
- **Issued**: Shows only invoices with status "issued"

### Persistence
- Filter selection automatically saved to localStorage
- Filter state restored on page reload
- Filter state maintained across navigation

## Troubleshooting

### Common Issues

**Filter not persisting**:
- Check browser localStorage support
- Verify localStorage permissions
- Check console for errors

**Filter not applying**:
- Verify invoice data structure
- Check filter logic implementation
- Ensure onFilterChange callback is working

**Performance issues**:
- Check invoice data volume
- Verify filter function efficiency
- Monitor component re-renders

### Debug Information

Enable debug logging:
```jsx
const debugMode = process.env.NODE_ENV === 'development';

if (debugMode) {
  console.log('Filter changed:', selectedFilter);
  console.log('Filtered invoices:', filteredInvoices.length);
}
```

## Performance Considerations

### Optimization Tips
- Use React.memo for component optimization
- Implement useCallback for filter functions
- Consider virtualization for large datasets

### Monitoring
- Track filter response times
- Monitor localStorage operations
- Check component render performance

## Browser Support

### Required Features
- localStorage API
- ES6+ JavaScript
- React 18.2.0

### Tested Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Security Notes

### Data Protection
- Filter state is non-sensitive UI preference
- No authentication required for filter operations
- No sensitive data stored in localStorage

### Input Validation
- Validate filter selection values
- Sanitize localStorage data
- Handle malformed data gracefully
