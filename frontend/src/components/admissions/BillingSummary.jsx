import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Divider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  Alert
} from '@mui/material';
import {
  Receipt as ReceiptIcon,
  Hotel as RoomIcon,
  AccessTime as TimeIcon,
  AttachMoney as MoneyIcon
} from '@mui/icons-material';

const BillingSummary = ({ billingSummary, admission }) => {
  if (!billingSummary) {
    return (
      <Alert severity="warning">
        No billing information available
      </Alert>
    );
  }

  const formatCurrency = (cents) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const formatDuration = (hours) => {
    if (hours < 24) {
      return `${hours.toFixed(1)} hours`;
    }
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return `${days} day${days !== 1 ? 's' : ''}${remainingHours > 0 ? ` and ${remainingHours.toFixed(1)} hours` : ''}`;
  };

  const totalCharges = billingSummary.total_charges_cents || 0;
  const baseCharges = billingSummary.base_charges_cents || 0;
  const additionalCharges = billingSummary.additional_charges_cents || 0;
  const taxes = billingSummary.taxes_cents || 0;
  const subtotal = baseCharges + additionalCharges;

  return (
    <Box>
      {/* Header */}
      <Box display="flex" alignItems="center" gap={1} mb={3}>
        <ReceiptIcon color="primary" />
        <Typography variant="h6">
          Billing Summary
        </Typography>
      </Box>

      {/* Room Information */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Room Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Box display="flex" alignItems="center" gap={1}>
                <RoomIcon />
                <Typography variant="body1">
                  <strong>Room:</strong> {billingSummary.breakdown?.room_info?.room_number || 'Unknown'}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body1">
                <strong>Type:</strong> 
                <Chip 
                  label={billingSummary.breakdown?.room_info?.room_type?.toUpperCase() || 'UNKNOWN'} 
                  size="small" 
                  color="primary" 
                  sx={{ ml: 1 }}
                />
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body1">
                <strong>Daily Rate:</strong> {formatCurrency(billingSummary.daily_rate_cents)}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box display="flex" alignItems="center" gap={1}>
                <TimeIcon />
                <Typography variant="body1">
                  <strong>Duration:</strong> {formatDuration(billingSummary.duration_hours)}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Billing Breakdown */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Billing Breakdown
        </Typography>
        
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell><strong>Description</strong></TableCell>
                <TableCell align="right"><strong>Amount</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell>
                  Room Charges ({formatDuration(billingSummary.duration_hours)})
                </TableCell>
                <TableCell align="right">
                  {formatCurrency(baseCharges)}
                </TableCell>
              </TableRow>
              
              {additionalCharges > 0 && (
                <TableRow>
                  <TableCell>
                    Additional Services
                  </TableCell>
                  <TableCell align="right">
                    {formatCurrency(additionalCharges)}
                  </TableCell>
                </TableRow>
              )}
              
              <TableRow>
                <TableCell>
                  <strong>Subtotal</strong>
                </TableCell>
                <TableCell align="right">
                  <strong>{formatCurrency(subtotal)}</strong>
                </TableCell>
              </TableRow>
              
              <TableRow>
                <TableCell>
                  Tax (8.5%)
                </TableCell>
                <TableCell align="right">
                  {formatCurrency(taxes)}
                </TableCell>
              </TableRow>
              
              <TableRow sx={{ backgroundColor: 'primary.light', color: 'primary.contrastText' }}>
                <TableCell>
                  <strong>Total</strong>
                </TableCell>
                <TableCell align="right">
                  <strong>{formatCurrency(totalCharges)}</strong>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Additional Information */}
      <Box mt={3}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Paper sx={{ p: 2, backgroundColor: 'success.light', color: 'success.contrastText' }}>
              <Box display="flex" alignItems="center" gap={1}>
                <MoneyIcon />
                <Typography variant="h6">
                  Total Charges
                </Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                {formatCurrency(totalCharges)}
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Paper sx={{ p: 2, backgroundColor: 'info.light', color: 'info.contrastText' }}>
              <Typography variant="h6" gutterBottom>
                Stay Duration
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {formatDuration(billingSummary.duration_hours)}
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Box>

      {/* Billing Notes */}
      <Box mt={3}>
        <Alert severity="info">
          <Typography variant="body2">
            <strong>Note:</strong> This billing summary is calculated based on the room's daily rate and 
            the duration of stay. Additional charges for services, medications, or procedures may be 
            added to the final invoice.
          </Typography>
        </Alert>
      </Box>

      {/* Rate Information */}
      {billingSummary.breakdown?.room_info && (
        <Box mt={2}>
          <Typography variant="body2" color="text.secondary">
            <strong>Rate Details:</strong> {billingSummary.breakdown.room_info.room_type} room at{' '}
            {formatCurrency(billingSummary.breakdown.room_info.daily_rate_cents)} per day
            {billingSummary.duration_hours < 24 && ' (prorated hourly)'}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default BillingSummary;
