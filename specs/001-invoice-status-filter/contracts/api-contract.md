# API Contract: Invoice Status Filter

**Feature**: Invoice Status Filter  
**Date**: 2024-01-15  
**Phase**: 1 - Design & Contracts

## Overview

This feature is a frontend-only component that uses client-side filtering. No backend API changes are required. The component consumes existing invoice data from the backend API.

## Existing API Endpoints (Consumed)

### GET /api/v1/invoices
**Purpose**: Retrieve all invoices for the management screen  
**Method**: GET  
**Authentication**: Required (JWT token)  
**Response**: Array of invoice objects

**Response Schema**:
```json
{
  "invoices": [
    {
      "id": "string",
      "invoiceNumber": "string",
      "patient": "string", 
      "status": "paid" | "issued",
      "amount": "number",
      "issuedDate": "string (ISO format)"
    }
  ]
}
```

**Status Codes**:
- 200: Success
- 401: Unauthorized
- 500: Server error

## Frontend Component Interface

### StatusFilterDropdown Component

**Props Interface**:
```typescript
interface StatusFilterDropdownProps {
  invoices: Invoice[];
  onFilterChange: (filteredInvoices: Invoice[]) => void;
  initialFilter?: string;
}
```

**State Interface**:
```typescript
interface FilterState {
  selectedFilter: 'all' | 'paid' | 'issued';
  isPersisted: boolean;
  lastUpdated: number;
}
```

**Methods Interface**:
```typescript
interface StatusFilterDropdownMethods {
  handleFilterChange: (filter: string) => void;
  loadFromStorage: () => void;
  saveToStorage: () => void;
  applyFilter: (invoices: Invoice[], filter: string) => Invoice[];
}
```

## Data Flow Contract

### Component Mount
1. Load filter state from localStorage
2. Apply saved filter to invoices
3. Display filtered results

### Filter Selection
1. Update component state
2. Apply filter to invoices array
3. Call onFilterChange callback
4. Save filter state to localStorage

### Error Handling
1. localStorage access fails → use default filter
2. Invalid filter state → reset to "all"
3. Filter application fails → show all invoices

## Performance Contract

### Response Time Requirements
- Filter application: <2 seconds
- localStorage operations: <100ms
- Component rendering: <1 second

### Data Volume Requirements
- Support up to 1000 invoices
- Filter state storage: <1KB
- Memory usage: Minimal (filtered array reference only)

## Browser Compatibility Contract

### Required Features
- localStorage API support
- ES6+ JavaScript features
- React 18.2.0 compatibility

### Graceful Degradation
- localStorage unavailable → use default filter
- Invalid stored data → reset to default
- Component errors → show all invoices

## Security Contract

### Data Protection
- No sensitive data in localStorage
- Filter state is non-sensitive UI preference
- No authentication required for filter operations

### Input Validation
- Filter selection must be valid option
- Invoice data must be properly typed
- localStorage data must be parseable

## Integration Contract

### Material-UI Integration
- Use Material-UI Select component
- Follow existing theme and styling
- Maintain accessibility standards

### React Integration
- Use React hooks (useState, useEffect)
- Follow React best practices
- Maintain component lifecycle

### Existing System Integration
- Integrate with existing invoice table
- Use existing invoice data structure
- Maintain existing user experience
