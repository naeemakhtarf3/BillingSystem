import React, { useState } from 'react';
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
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
  Chip,
  Paper,
  Divider
} from '@mui/material';
import {
  Build as MaintenanceIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  Description as DescriptionIcon,
  Hotel as RoomIcon
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

const schema = yup.object({
  maintenance_type: yup.string().required('Maintenance type is required'),
  description: yup.string().required('Description is required'),
  scheduled_date: yup.date().required('Scheduled date is required'),
  estimated_duration: yup.number().required('Estimated duration is required').min(1, 'Duration must be at least 1 hour'),
  assigned_staff: yup.string().required('Assigned staff is required'),
  priority: yup.string().required('Priority is required')
});

const MaintenanceForm = ({ room, open, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isValid }
  } = useForm({
    resolver: yupResolver(schema),
    mode: 'onChange',
    defaultValues: {
      maintenance_type: '',
      description: '',
      scheduled_date: new Date().toISOString().slice(0, 16),
      estimated_duration: 2,
      assigned_staff: '',
      priority: 'medium'
    }
  });

  const maintenanceTypes = [
    { value: 'cleaning', label: 'Deep Cleaning' },
    { value: 'repair', label: 'Repair Work' },
    { value: 'inspection', label: 'Safety Inspection' },
    { value: 'upgrade', label: 'Equipment Upgrade' },
    { value: 'pest_control', label: 'Pest Control' },
    { value: 'other', label: 'Other' }
  ];

  const priorityLevels = [
    { value: 'low', label: 'Low', color: 'success' },
    { value: 'medium', label: 'Medium', color: 'warning' },
    { value: 'high', label: 'High', color: 'error' },
    { value: 'urgent', label: 'Urgent', color: 'error' }
  ];

  const staffMembers = [
    { id: 1, name: 'John Smith', role: 'Maintenance Technician' },
    { id: 2, name: 'Sarah Johnson', role: 'Facilities Manager' },
    { id: 3, name: 'Mike Wilson', role: 'Maintenance Supervisor' },
    { id: 4, name: 'Lisa Brown', role: 'Cleaning Specialist' }
  ];

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      setError(null);
      
      // This would call the backend API to schedule maintenance
      console.log('Scheduling maintenance for room:', room.id, 'with data:', data);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      setError(err.message || 'Failed to schedule maintenance');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    reset();
    setError(null);
    onClose();
  };

  const getPriorityColor = (priority) => {
    const level = priorityLevels.find(p => p.value === priority);
    return level?.color || 'default';
  };

  if (!room) return null;

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <MaintenanceIcon color="warning" />
          <Typography variant="h6">
            Schedule Maintenance
          </Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box>
          {/* Room Information */}
          <Paper sx={{ p: 2, mb: 3, backgroundColor: 'grey.50' }}>
            <Typography variant="h6" gutterBottom>
              Room Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Box display="flex" alignItems="center" gap={1}>
                  <RoomIcon />
                  <Typography variant="body1">
                    <strong>Room:</strong> {room.room_number}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body1">
                  <strong>Type:</strong> 
                  <Chip 
                    label={room.type.toUpperCase()} 
                    size="small" 
                    color="primary" 
                    sx={{ ml: 1 }}
                  />
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body1">
                  <strong>Current Status:</strong> 
                  <Chip 
                    label={room.status.toUpperCase()} 
                    size="small" 
                    color="success" 
                    sx={{ ml: 1 }}
                  />
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body1">
                  <strong>Daily Rate:</strong> ${(room.daily_rate_cents / 100).toFixed(2)}
                </Typography>
              </Grid>
            </Grid>
          </Paper>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit(onSubmit)}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Controller
                  name="maintenance_type"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.maintenance_type}>
                      <InputLabel>Maintenance Type</InputLabel>
                      <Select {...field} label="Maintenance Type">
                        {maintenanceTypes.map((type) => (
                          <MenuItem key={type.value} value={type.value}>
                            {type.label}
                          </MenuItem>
                        ))}
                      </Select>
                      {errors.maintenance_type && (
                        <Typography variant="caption" color="error" sx={{ mt: 1, ml: 2 }}>
                          {errors.maintenance_type.message}
                        </Typography>
                      )}
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="priority"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.priority}>
                      <InputLabel>Priority</InputLabel>
                      <Select {...field} label="Priority">
                        {priorityLevels.map((level) => (
                          <MenuItem key={level.value} value={level.value}>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Chip
                                label={level.label}
                                size="small"
                                color={level.color}
                                variant="outlined"
                              />
                            </Box>
                          </MenuItem>
                        ))}
                      </Select>
                      {errors.priority && (
                        <Typography variant="caption" color="error" sx={{ mt: 1, ml: 2 }}>
                          {errors.priority.message}
                        </Typography>
                      )}
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="scheduled_date"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Scheduled Date & Time"
                      type="datetime-local"
                      fullWidth
                      error={!!errors.scheduled_date}
                      helperText={errors.scheduled_date?.message}
                      InputLabelProps={{ shrink: true }}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="estimated_duration"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Estimated Duration (hours)"
                      type="number"
                      fullWidth
                      error={!!errors.estimated_duration}
                      helperText={errors.estimated_duration?.message}
                      inputProps={{ min: 1, max: 24 }}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Controller
                  name="assigned_staff"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.assigned_staff}>
                      <InputLabel>Assigned Staff</InputLabel>
                      <Select {...field} label="Assigned Staff">
                        {staffMembers.map((staff) => (
                          <MenuItem key={staff.id} value={staff.id}>
                            <Box>
                              <Typography variant="body2" fontWeight="medium">
                                {staff.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {staff.role}
                              </Typography>
                            </Box>
                          </MenuItem>
                        ))}
                      </Select>
                      {errors.assigned_staff && (
                        <Typography variant="caption" color="error" sx={{ mt: 1, ml: 2 }}>
                          {errors.assigned_staff.message}
                        </Typography>
                      )}
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid item xs={12}>
                <Controller
                  name="description"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Description"
                      multiline
                      rows={4}
                      fullWidth
                      error={!!errors.description}
                      helperText={errors.description?.message || 'Provide detailed description of maintenance work to be performed'}
                      placeholder="Describe the maintenance work, equipment needed, special requirements, etc."
                    />
                  )}
                />
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            {/* Maintenance Checklist */}
            <Paper sx={{ p: 2, backgroundColor: 'info.light' }}>
              <Typography variant="h6" gutterBottom>
                Pre-Maintenance Checklist
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Ensure room is unoccupied and available<br/>
                • Notify relevant staff of maintenance schedule<br/>
                • Prepare necessary equipment and supplies<br/>
                • Update room status to maintenance<br/>
                • Schedule follow-up inspection if needed
              </Typography>
            </Paper>
          </form>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button 
          variant="contained" 
          onClick={handleSubmit(onSubmit)}
          disabled={loading || !isValid}
          startIcon={loading ? <CircularProgress size={20} /> : <ScheduleIcon />}
        >
          {loading ? 'Scheduling...' : 'Schedule Maintenance'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default MaintenanceForm;
