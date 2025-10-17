/**
 * TypeScript interfaces for Invoice Status Filter feature
 * 
 * This file defines the type interfaces for the StatusFilterDropdown component
 * and related invoice data structures.
 */

/**
 * Invoice entity interface
 * Represents a billing document in the clinic billing system
 */
export interface Invoice {
  id: string;
  invoiceNumber: string;
  patient: string;
  status: 'paid' | 'issued';
  amount: number;
  issuedDate: string; // ISO format date string
}

/**
 * Filter state interface
 * Represents the current filter selection and persistence state
 */
export interface FilterState {
  selectedFilter: 'all' | 'paid' | 'issued';
  isPersisted: boolean;
  lastUpdated: number;
}

/**
 * StatusFilterDropdown component props interface
 */
export interface StatusFilterDropdownProps {
  invoices: Invoice[];
  onFilterChange: (filteredInvoices: Invoice[]) => void;
  initialFilter?: string;
}

/**
 * Filter change event interface
 */
export interface FilterChangeEvent {
  target: {
    value: string;
  };
}

/**
 * LocalStorage utility interface
 */
export interface LocalStorageFilterData {
  selectedFilter: 'all' | 'paid' | 'issued';
  timestamp: number;
}
