import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Paper,
  Divider,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  PersonRemove as DischargeIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Receipt as ReceiptIcon,
  Hotel as RoomIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useAdmissionContext } from '../../contexts/AdmissionContext';
import BillingSummary from './BillingSummary';

const schema = yup.object({
  discharge_date: yup.date().required('Discharge date is required'),
  discharge_reason: yup.string().required('Discharge reason is required'),
  discharge_notes: yup.string().max(500, 'Discharge notes cannot exceed 500 characters')
});

const DischargeForm = ({ admission, onSuccess, onCancel }) => {
  const { dischargePatient, loading } = useAdmissionContext();
  const [error, setError] = useState(null);
  const [showBillingSummary, setShowBillingSummary] = useState(false);
  const [billingSummary, setBillingSummary] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(false);

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting, isValid }
  } = useForm({
    resolver: yupResolver(schema),
    mode: 'onChange',
    defaultValues: {
      discharge_date: new Date().toISOString().slice(0, 16),
      discharge_reason: '',
      discharge_notes: ''
    }
  });

  const dischargeReasons = [
    { value: 'recovery', label: 'Recovery Complete' },
    { value: 'transfer', label: 'Transfer to Another Facility' },
    { value: 'patient_request', label: 'Patient Request' },
    { value: 'medical_necessity', label: 'Medical Necessity' },
    { value: 'other', label: 'Other' }
  ];

  const onSubmit = async (data) => {
    try {
      setError(null);
      
      // Calculate billing summary first
      const billingData = await calculateBillingSummary(data);
      setBillingSummary(billingData);
      setShowBillingSummary(true);
      
    } catch (err) {
      setError(err.message || 'Failed to calculate billing summary');
    }
  };

  const calculateBillingSummary = async (dischargeData) => {
    // This would call the backend to calculate billing
    // For now, return mock data
    const durationHours = (new Date(dischargeData.discharge_date) - new Date(admission.admission_date)) / (1000 * 60 * 60);
    const dailyRate = admission.room?.daily_rate_cents || 15000; // Default rate
    
    let totalCharges = 0;
    if (durationHours < 24) {
      // Hourly rate for same-day stays
      totalCharges = (dailyRate / 24) * durationHours;
    } else {
      // Daily rate for multi-day stays
      const days = Math.ceil(durationHours / 24);
      totalCharges = dailyRate * days;
    }
    
    return {
      total_charges_cents: Math.round(totalCharges),
      duration_hours: durationHours,
      daily_rate_cents: dailyRate,
      base_charges_cents: Math.round(totalCharges),
      additional_charges_cents: 0,
      taxes_cents: Math.round(totalCharges * 0.085), // 8.5% tax
      breakdown: {
        room_info: {
          room_number: admission.room?.room_number || 'Unknown',
          room_type: admission.room?.type || 'standard',
          daily_rate_cents: dailyRate
        },
        duration: {
          hours: durationHours,
          formatted: formatDuration(durationHours)
        }
      }
    };
  };

  const formatDuration = (hours) => {
    if (hours < 24) {
      return `${hours.toFixed(1)} hours`;
    }
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return `${days} day${days !== 1 ? 's' : ''}${remainingHours > 0 ? ` and ${remainingHours.toFixed(1)} hours` : ''}`;
  };

  const handleConfirmDischarge = async () => {
    try {
      setError(null);
      const formData = watch();
      
      const result = await dischargePatient(admission.id, {
        discharge_date: new Date(formData.discharge_date),
        discharge_reason: formData.discharge_reason,
        discharge_notes: formData.discharge_notes
      });
      
      setShowConfirmation(false);
      setShowBillingSummary(false);
      
      if (onSuccess) {
        onSuccess(result);
      }
    } catch (err) {
      setError(err.message || 'Failed to discharge patient');
    }
  };

  const handleCancel = () => {
    setShowBillingSummary(false);
    setShowConfirmation(false);
    if (onCancel) {
      onCancel();
    }
  };

  if (!admission) {
    return (
      <Alert severity="error">
        No admission selected for discharge
      </Alert>
    );
  }

  return (
    <>
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={3}>
            <DischargeIcon color="primary" />
            <Typography variant="h5" component="h2">
              Discharge Patient
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Admission Summary */}
          <Paper sx={{ p: 2, mb: 3, backgroundColor: 'grey.50' }}>
            <Typography variant="h6" gutterBottom>
              Admission Details
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Box display="flex" alignItems="center" gap={1}>
                  <PersonIcon />
                  <Typography variant="body1">
                    <strong>Patient ID:</strong> {admission.patient_id}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box display="flex" alignItems="center" gap={1}>
                  <RoomIcon />
                  <Typography variant="body1">
                    <strong>Room:</strong> {admission.room?.room_number || 'Unknown'}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body1">
                  <strong>Admission Date:</strong> {new Date(admission.admission_date).toLocaleString()}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body1">
                  <strong>Room Type:</strong> 
                  <Chip 
                    label={admission.room?.type?.toUpperCase() || 'UNKNOWN'} 
                    size="small" 
                    color="primary" 
                    sx={{ ml: 1 }}
                  />
                </Typography>
              </Grid>
            </Grid>
          </Paper>

          <form onSubmit={handleSubmit(onSubmit)}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="discharge_date"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Discharge Date & Time"
                      type="datetime-local"
                      fullWidth
                      error={!!errors.discharge_date}
                      helperText={errors.discharge_date?.message}
                      InputLabelProps={{ shrink: true }}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="discharge_reason"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.discharge_reason}>
                      <InputLabel>Discharge Reason</InputLabel>
                      <Select {...field} label="Discharge Reason">
                        {dischargeReasons.map((reason) => (
                          <MenuItem key={reason.value} value={reason.value}>
                            {reason.label}
                          </MenuItem>
                        ))}
                      </Select>
                      {errors.discharge_reason && (
                        <Typography variant="caption" color="error" sx={{ mt: 1, ml: 2 }}>
                          {errors.discharge_reason.message}
                        </Typography>
                      )}
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12}>
                <Controller
                  name="discharge_notes"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Discharge Notes"
                      multiline
                      rows={4}
                      fullWidth
                      error={!!errors.discharge_notes}
                      helperText={errors.discharge_notes?.message || 'Optional notes about the discharge'}
                      placeholder="Enter any additional notes about the discharge..."
                    />
                  )}
                />
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Button
                variant="outlined"
                startIcon={<CancelIcon />}
                onClick={handleCancel}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                startIcon={isSubmitting ? <CircularProgress size={20} /> : <ReceiptIcon />}
                disabled={isSubmitting || !isValid}
              >
                {isSubmitting ? 'Calculating...' : 'Calculate Billing & Continue'}
              </Button>
            </Box>
          </form>
        </CardContent>
      </Card>

      {/* Billing Summary Dialog */}
      <Dialog 
        open={showBillingSummary} 
        onClose={() => setShowBillingSummary(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <ReceiptIcon />
            <Typography variant="h6">Billing Summary</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {billingSummary && (
            <BillingSummary 
              billingSummary={billingSummary}
              admission={admission}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowBillingSummary(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={() => setShowConfirmation(true)}
            startIcon={<DischargeIcon />}
          >
            Proceed with Discharge
          </Button>
        </DialogActions>
      </Dialog>

      {/* Confirmation Dialog */}
      <Dialog 
        open={showConfirmation} 
        onClose={() => setShowConfirmation(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Confirm Discharge
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            Are you sure you want to discharge this patient? This action will:
          </Typography>
          <ul>
            <li>Update the admission status to discharged</li>
            <li>Calculate and generate billing</li>
            <li>Update the room status to available</li>
            <li>Create an invoice for the patient</li>
          </ul>
          <Typography variant="body2" color="text.secondary">
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmation(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            color="error"
            onClick={handleConfirmDischarge}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <DischargeIcon />}
          >
            {loading ? 'Discharging...' : 'Confirm Discharge'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DischargeForm;
