# Data Model: Invoice Status Filter

**Feature**: Invoice Status Filter  
**Date**: 2024-01-15  
**Phase**: 1 - Design & Contracts

## Entities

### Invoice Entity (Existing)
**Purpose**: Represents a billing document in the system  
**Source**: Existing entity from the clinic billing system

**Attributes**:
- `id`: string - Unique identifier for the invoice
- `invoiceNumber`: string - Human-readable invoice number (e.g., "CLIN-2025-0004")
- `patient`: string - Patient name (e.g., "John Smith")
- `status`: string - Invoice status ("paid" or "issued")
- `amount`: number - Invoice amount in USD
- `issuedDate`: string - Date when invoice was issued (ISO format)

**Relationships**:
- Belongs to Patient entity
- Has many Payment entities (for paid invoices)

**Validation Rules**:
- `status` must be either "paid" or "issued"
- `amount` must be positive number
- `invoiceNumber` must be unique
- `issuedDate` must be valid ISO date string

### Filter State Entity (New)
**Purpose**: Represents the current filter selection and persistence state  
**Source**: New entity for this feature

**Attributes**:
- `selectedFilter`: string - Current filter selection ("all", "paid", "issued")
- `lastUpdated`: number - Timestamp of last filter change
- `isPersisted`: boolean - Whether filter state is saved to localStorage

**Validation Rules**:
- `selectedFilter` must be one of: "all", "paid", "issued"
- `lastUpdated` must be valid timestamp
- `isPersisted` must be boolean

**State Transitions**:
- Initial state: `selectedFilter: "all"`, `isPersisted: false`
- After user selection: `selectedFilter: userChoice`, `isPersisted: true`
- After localStorage save: `isPersisted: true`
- After localStorage load: `selectedFilter: storedValue`, `isPersisted: true`

## Data Flow

### Filter Application Flow
1. User selects filter option from dropdown
2. Filter state updates in component state
3. Filter function applied to invoices array
4. Filtered results displayed in table
5. Filter state saved to localStorage

### Persistence Flow
1. Component mounts
2. Check localStorage for saved filter state
3. If found, apply saved filter
4. If not found, use default "all" filter
5. Save any filter changes to localStorage

### Error Handling Flow
1. localStorage access fails
2. Fall back to default "all" filter
3. Log warning to console
4. Continue with client-side filtering

## Data Relationships

### Invoice to Filter State
- One-to-many: One filter state can filter many invoices
- Filter state determines which invoices are visible
- Invoices are filtered based on status attribute

### Filter State to localStorage
- One-to-one: One filter state per browser session
- localStorage key: "invoiceStatusFilter"
- localStorage value: JSON string of filter state

## Data Validation

### Input Validation
- Filter selection must be valid option
- Invoice data must have required attributes
- localStorage data must be parseable JSON

### Output Validation
- Filtered results must be array of Invoice objects
- Empty results must show appropriate message
- Filter state must be consistent with UI

## Data Constraints

### Performance Constraints
- Filter operation must complete in <2 seconds
- Support up to 1000 invoices
- localStorage operations must complete in <100ms

### Storage Constraints
- localStorage key: "invoiceStatusFilter"
- Maximum storage size: 1KB
- Data format: JSON string

### Browser Constraints
- Must work in Chrome, Firefox, Safari, Edge
- Graceful degradation if localStorage unavailable
- No external dependencies for data operations
