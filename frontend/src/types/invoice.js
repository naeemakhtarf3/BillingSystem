/**
 * JavaScript type definitions for Invoice Status Filter feature
 * 
 * This file provides JSDoc type definitions for the StatusFilterDropdown component
 * and related invoice data structures. This is the JavaScript equivalent of invoice.ts
 */

/**
 * @typedef {Object} Invoice
 * @property {string} id - Unique invoice identifier
 * @property {string} invoiceNumber - Invoice number (e.g., "CLIN-2025-0001")
 * @property {string} patient - Patient name
 * @property {'paid'|'issued'} status - Invoice status
 * @property {number} amount - Invoice amount in major currency units
 * @property {string} issuedDate - ISO format date string
 */

/**
 * @typedef {Object} FilterState
 * @property {'all'|'paid'|'issued'} selectedFilter - Current filter selection
 * @property {boolean} isPersisted - Whether the filter state is persisted
 * @property {number} lastUpdated - Timestamp of last update
 */

/**
 * @typedef {Object} StatusFilterDropdownProps
 * @property {Invoice[]} invoices - Array of invoice objects to filter
 * @property {function(Invoice[]): void} onFilterChange - Callback when filter changes
 * @property {string} [initialFilter='all'] - Initial filter selection
 * @property {boolean} [showNoResultsMessage=true] - Whether to show empty state message
 */

/**
 * @typedef {Object} FilterChangeEvent
 * @property {Object} target - Event target
 * @property {string} target.value - Selected filter value
 */

/**
 * @typedef {Object} LocalStorageFilterData
 * @property {'all'|'paid'|'issued'} selectedFilter - Filter value to persist
 * @property {number} timestamp - Persistence timestamp
 */

// Export empty object to make this a valid module
export {};
