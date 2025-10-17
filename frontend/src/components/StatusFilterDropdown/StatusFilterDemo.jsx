import React, { useState } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import StatusFilterDropdown from './index';

/**
 * Demo component to test StatusFilterDropdown functionality
 * This component demonstrates User Story 1: Filter Invoices by Status
 */
const StatusFilterDemo = () => {
  // Sample invoice data for testing
  const [allInvoices] = useState([
    {
      id: '1',
      invoiceNumber: 'CLIN-2025-0001',
      patient: 'John Smith',
      status: 'paid',
      amount: 150.00,
      issuedDate: '2025-01-10T10:30:00Z'
    },
    {
      id: '2',
      invoiceNumber: 'CLIN-2025-0002',
      patient: 'Jane Doe',
      status: 'issued',
      amount: 200.00,
      issuedDate: '2025-01-11T14:15:00Z'
    },
    {
      id: '3',
      invoiceNumber: 'CLIN-2025-0003',
      patient: 'Bob Johnson',
      status: 'paid',
      amount: 75.50,
      issuedDate: '2025-01-12T09:45:00Z'
    },
    {
      id: '4',
      invoiceNumber: 'CLIN-2025-0004',
      patient: 'Alice Brown',
      status: 'issued',
      amount: 300.00,
      issuedDate: '2025-01-13T16:20:00Z'
    }
  ]);

  const [filteredInvoices, setFilteredInvoices] = useState(allInvoices);

  const handleFilterChange = (filtered) => {
    setFilteredInvoices(filtered);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Invoice Status Filter Demo
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <StatusFilterDropdown
          invoices={allInvoices}
          onFilterChange={handleFilterChange}
          showNoResultsMessage={true}
        />
      </Box>

      <Typography variant="h6" gutterBottom>
        Filtered Results ({filteredInvoices.length} invoices)
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Invoice #</TableCell>
              <TableCell>Patient</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Issued Date</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredInvoices.map((invoice) => (
              <TableRow key={invoice.id}>
                <TableCell>{invoice.invoiceNumber}</TableCell>
                <TableCell>{invoice.patient}</TableCell>
                <TableCell>
                  <Typography
                    variant="body2"
                    sx={{
                      color: invoice.status === 'paid' ? 'green' : 'orange',
                      fontWeight: 'bold'
                    }}
                  >
                    {invoice.status.toUpperCase()}
                  </Typography>
                </TableCell>
                <TableCell>${invoice.amount.toFixed(2)}</TableCell>
                <TableCell>
                  {new Date(invoice.issuedDate).toLocaleDateString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredInvoices.length === 0 && (
        <Box sx={{ mt: 2, p: 2, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No invoices match the selected filter.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default StatusFilterDemo;
