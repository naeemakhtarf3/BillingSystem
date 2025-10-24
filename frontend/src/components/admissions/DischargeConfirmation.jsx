import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Paper,
  Divider,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  CheckCircle as SuccessIcon,
  PersonRemove as DischargeIcon,
  Receipt as ReceiptIcon,
  Hotel as RoomIcon,
  Person as PersonIcon,
  AccessTime as TimeIcon,
  AttachMoney as MoneyIcon,
  Print as PrintIcon,
  Email as EmailIcon
} from '@mui/icons-material';

const DischargeConfirmation = ({ 
  dischargeResult, 
  onClose, 
  onPrint, 
  onEmail,
  loading = false 
}) => {
  if (!dischargeResult) {
    return null;
  }

  const formatCurrency = (cents) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (hours) => {
    if (hours < 24) {
      return `${hours.toFixed(1)} hours`;
    }
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return `${days} day${days !== 1 ? 's' : ''}${remainingHours > 0 ? ` and ${remainingHours.toFixed(1)} hours` : ''}`;
  };

  return (
    <Dialog 
      open={true} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <SuccessIcon color="success" />
          <Typography variant="h6">
            Discharge Successful
          </Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box>
          {/* Success Message */}
          <Alert severity="success" sx={{ mb: 3 }}>
            <Typography variant="body1" fontWeight="medium">
              Patient has been successfully discharged!
            </Typography>
            <Typography variant="body2">
              The room has been updated to available status and billing has been calculated.
            </Typography>
          </Alert>

          {/* Discharge Summary */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Discharge Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <PersonIcon />
                    <Typography variant="body1">
                      <strong>Patient ID:</strong> {dischargeResult.patient_id}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <RoomIcon />
                    <Typography variant="body1">
                      <strong>Room:</strong> {dischargeResult.room_id}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <TimeIcon />
                    <Typography variant="body1">
                      <strong>Discharge Date:</strong> {formatDate(dischargeResult.discharge_date)}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <ReceiptIcon />
                    <Typography variant="body1">
                      <strong>Invoice ID:</strong> {dischargeResult.invoice_id}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Billing Summary */}
          {dischargeResult.billing_summary && (
            <Paper sx={{ p: 2, mb: 3, backgroundColor: 'grey.50' }}>
              <Typography variant="h6" gutterBottom>
                Billing Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body1">
                    <strong>Duration:</strong> {formatDuration(dischargeResult.billing_summary.duration_hours)}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body1">
                    <strong>Daily Rate:</strong> {formatCurrency(dischargeResult.billing_summary.daily_rate_cents)}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body1">
                    <strong>Base Charges:</strong> {formatCurrency(dischargeResult.billing_summary.base_charges_cents || 0)}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body1">
                    <strong>Additional Charges:</strong> {formatCurrency(dischargeResult.billing_summary.additional_charges_cents || 0)}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body1">
                    <strong>Taxes:</strong> {formatCurrency(dischargeResult.billing_summary.taxes_cents || 0)}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <MoneyIcon />
                    <Typography variant="h6" color="primary">
                      <strong>Total:</strong> {formatCurrency(dischargeResult.billing_summary.total_charges_cents)}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          )}

          {/* Room Status Update */}
          {dischargeResult.room_status_updated && (
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="body1">
                <strong>Room Status Updated:</strong> The room has been automatically updated to available status.
              </Typography>
            </Alert>
          )}

          {/* Next Steps */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Next Steps
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <ReceiptIcon />
                </ListItemIcon>
                <ListItemText 
                  primary="Invoice Generated" 
                  secondary={`Invoice ${dischargeResult.invoice_id} has been created and is ready for payment processing.`}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <RoomIcon />
                </ListItemIcon>
                <ListItemText 
                  primary="Room Available" 
                  secondary="The room is now available for new admissions."
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <PersonIcon />
                </ListItemIcon>
                <ListItemText 
                  primary="Patient Records" 
                  secondary="Patient admission records have been updated with discharge information."
                />
              </ListItem>
            </List>
          </Paper>

          {/* Action Buttons */}
          <Box mt={3} display="flex" gap={2} flexWrap="wrap">
            <Button
              variant="outlined"
              startIcon={<PrintIcon />}
              onClick={onPrint}
              disabled={loading}
            >
              Print Discharge Summary
            </Button>
            <Button
              variant="outlined"
              startIcon={<EmailIcon />}
              onClick={onEmail}
              disabled={loading}
            >
              Email to Patient
            </Button>
            <Button
              variant="contained"
              startIcon={<ReceiptIcon />}
              onClick={() => window.open(`/invoices/${dischargeResult.invoice_id}`, '_blank')}
              disabled={loading}
            >
              View Invoice
            </Button>
          </Box>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Close
        </Button>
        <Button 
          variant="contained" 
          onClick={onClose}
          disabled={loading}
        >
          {loading ? <CircularProgress size={20} /> : 'Done'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DischargeConfirmation;
