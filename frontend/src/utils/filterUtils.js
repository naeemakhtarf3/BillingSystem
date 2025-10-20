// Note: Invoice type is defined in ../types/invoice.ts
// This is a JavaScript file, so we use JSDoc for type annotations

/**
 * Filter utility functions for Invoice Status Filter
 * 
 * Provides efficient client-side filtering operations for invoice data
 */

/**
 * Apply status filter to invoices array
 * @param {Array} invoices - Array of invoices to filter
 * @param {string} filter - Filter value ('all', 'paid', 'issued')
 * @returns {Array} Filtered array of invoices
 */
export const applyStatusFilter = (invoices, filter) => {
  if (!Array.isArray(invoices)) {
    console.warn('applyStatusFilter: invoices must be an array');
    return [];
  }
  
  if (filter === 'all') {
    return invoices;
  }
  
  if (!['paid', 'issued'].includes(filter)) {
    console.warn(`applyStatusFilter: invalid filter value "${filter}"`);
    return invoices;
  }
  
  return invoices.filter(invoice => {
    if (!invoice || typeof invoice.status !== 'string') {
      return false;
    }
    return invoice.status === filter;
  });
};

/**
 * Get filter statistics for invoices array
 * @param {Array} invoices - Array of invoices to analyze
 * @returns {Object} Filter statistics
 */
export const getFilterStats = (invoices) => {
  if (!Array.isArray(invoices)) {
    return { total: 0, paid: 0, issued: 0 };
  }
  
  const stats = {
    total: invoices.length,
    paid: 0,
    issued: 0
  };
  
  invoices.forEach(invoice => {
    if (invoice && invoice.status === 'paid') {
      stats.paid++;
    } else if (invoice && invoice.status === 'issued') {
      stats.issued++;
    }
  });
  
  return stats;
};

/**
 * Validate invoice object structure
 * @param {Object} invoice - Invoice object to validate
 * @returns {boolean} Validation result
 */
export const validateInvoice = (invoice) => {
  if (!invoice || typeof invoice !== 'object') {
    return false;
  }
  
  const requiredFields = ['id', 'invoiceNumber', 'patient', 'status', 'amount', 'issuedDate'];
  
  for (const field of requiredFields) {
    if (!(field in invoice)) {
      return false;
    }
  }
  
  // Validate status field
  if (!['paid', 'issued'].includes(invoice.status)) {
    return false;
  }
  
  // Validate amount field
  if (typeof invoice.amount !== 'number' || invoice.amount < 0) {
    return false;
  }
  
  return true;
};

/**
 * Filter and validate invoices array
 * @param {Array} invoices - Array of invoices to filter and validate
 * @param {string} filter - Filter value ('all', 'paid', 'issued')
 * @returns {Object} Filtered results with validation info
 */
export const filterAndValidateInvoices = (invoices, filter) => {
  if (!Array.isArray(invoices)) {
    return {
      filtered: [],
      valid: [],
      invalid: [],
      stats: { total: 0, paid: 0, issued: 0 }
    };
  }
  
  const valid = [];
  const invalid = [];
  
  // Separate valid and invalid invoices
  invoices.forEach(invoice => {
    if (validateInvoice(invoice)) {
      valid.push(invoice);
    } else {
      invalid.push(invoice);
    }
  });
  
  // Apply filter to valid invoices
  const filtered = applyStatusFilter(valid, filter);
  
  return {
    filtered,
    valid,
    invalid,
    stats: getFilterStats(valid)
  };
};

/**
 * Check if filter results are empty
 * @param {Array} filteredInvoices - Filtered invoices array
 * @returns {boolean} Empty results status
 */
export const isEmptyResults = (filteredInvoices) => {
  return !Array.isArray(filteredInvoices) || filteredInvoices.length === 0;
};

/**
 * Get filter options configuration
 * @returns {Array} Filter options array
 */
export const getFilterOptions = () => {
  return [
    { value: 'all', label: 'All' },
    { value: 'paid', label: 'Paid' },
    { value: 'issued', label: 'Issued' }
  ];
};

/**
 * Debounce filter application for performance optimization
 * @param {Function} filterFunction - Filter function to debounce
 * @param {number} delay - Debounce delay in milliseconds
 * @returns {Function} Debounced filter function
 */
export const debounceFilter = (filterFunction, delay = 300) => {
  let timeoutId;
  
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => filterFunction(...args), delay);
  };
};
