import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, CircularProgress, Table, TableHead, TableRow, TableCell, TableBody, Box, TextField } from '@mui/material';
import ExportControls from '../common/ExportControls';
import { fetchOutstanding } from '../../services/reportService';

export default function OutstandingPayments() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({ min_days_overdue: '', min_amount: '' });

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    fetchOutstanding({
      min_days_overdue: filters.min_days_overdue || undefined,
      min_amount: filters.min_amount || undefined,
    })
      .then((res) => {
        if (!isMounted) return;
        setItems(res.items || []);
      })
      .finally(() => isMounted && setLoading(false));
    return () => {
      isMounted = false;
    };
  }, [filters.min_days_overdue, filters.min_amount]);
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const handleExport = async () => {
    const params = new URLSearchParams({ ...filters, format: 'csv' }).toString();
    window.open(`${API_BASE_URL}/api/v1/reports/outstanding?${params}`, '_blank');
  };

  return (
    <Card aria-label="Outstanding payments">
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Outstanding Payments</Typography>
          <ExportControls onExport={handleExport} />
        </Box>
        <Box display="flex" gap={2} mb={2}>
          <TextField
            label="Min Days Overdue"
            type="number"
            value={filters.min_days_overdue}
            onChange={(e) => setFilters((f) => ({ ...f, min_days_overdue: e.target.value }))}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            label="Min Amount ($)"
            type="number"
            value={filters.min_amount}
            onChange={(e) => setFilters((f) => ({ ...f, min_amount: e.target.value }))}
            InputLabelProps={{ shrink: true }}
          />
        </Box>
        {loading ? (
          <CircularProgress size={24} aria-label="Loading outstanding" />
        ) : (
          <Table size="small" aria-label="Outstanding payments table">
            <TableHead>
              <TableRow>
                <TableCell>Patient ID</TableCell>
                <TableCell>Invoice ID</TableCell>
                <TableCell align="right">Amount Due</TableCell>
                <TableCell align="right">Days Overdue</TableCell>
                <TableCell>Last Payment</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((row, idx) => (
                <TableRow key={idx} tabIndex={0}>
                  <TableCell>{row.patientId}</TableCell>
                  <TableCell>{row.invoiceId}</TableCell>
                  <TableCell align="right">${row.amountDue.toFixed(2)}</TableCell>
                  <TableCell align="right">{row.daysOverdue}</TableCell>
                  <TableCell>{row.lastPaymentDate || '-'}</TableCell>
                  <TableCell>{row.status}</TableCell>
                </TableRow>
              ))}
              {items.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6}>No outstanding payments found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}


