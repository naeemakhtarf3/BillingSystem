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
  Snackbar
} from '@mui/material';
import {
  PersonAdd as PersonAddIcon,
  Hotel as RoomIcon,
  Person as PersonIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useRoomContext } from '../../contexts/RoomContext';
import { useAdmissionContext } from '../../contexts/AdmissionContext';
import patientService from '../../services/patientApi';
import authService from '../../services/authApi';

const schema = yup.object({
  patient_id: yup
    .string()
    .required('Patient is required')
    .uuid('Patient ID must be a valid UUID'),
  room_id: yup
    .number()
    .required('Room is required')
    .positive('Room ID must be positive')
    .integer('Room ID must be an integer'),
  staff_id: yup
    .string()
    .required('Staff member is required')
    .uuid('Staff ID must be a valid UUID'),
  admission_date: yup
    .date()
    .required('Admission date is required')
    .min(new Date(), 'Admission date cannot be in the past')
    .max(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), 'Admission date cannot be more than 7 days in the future')
});

const AdmissionForm = ({ onSuccess, onCancel }) => {
  const { rooms, fetchRooms } = useRoomContext();
  const { createAdmission, loading } = useAdmissionContext();
  const [patients, setPatients] = useState([]);
  const [staff, setStaff] = useState([]);
  const [availableRooms, setAvailableRooms] = useState([]);
  const [error, setError2] = useState(null);
 
  const {
    control,
    handleSubmit,
    watch,
    setValue,
    setError,
    clearErrors,
    formState: { errors, isSubmitting, isValid, isDirty }
  } = useForm({
    resolver: yupResolver(schema),
    mode: 'onChange', // Real-time validation
    defaultValues: {
      admission_date: new Date().toISOString().slice(0, 16)
    }
  });

  const selectedRoomId = watch('room_id');

  useEffect(() => {
    fetchRooms({ available_only: true });
    // Fetch patients from API
    const fetchPatients = async () => {
      try {
        const patientsData = await patientService.getPatients();
        setPatients(patientsData);
      } catch (error) {
        console.error('Failed to fetch patients:', error);
        setError('Failed to load patients. Please try again.');
      }
    };
    fetchPatients();

    // Fetch staff from API
    const fetchStaff = async () => {
      try {
        const staffData = await authService.getStaff();
        console.log(staffData);
        
        setStaff(staffData);
      } catch (error) {
        console.error('Failed to fetch staff:', error);
        setError('Failed to load staff. Please try again.');
      }
    };
    fetchStaff();
  }, []);

  useEffect(() => {
    setAvailableRooms(rooms.filter(room => room.status.toLowerCase() === 'available'));
    
    
  }, [rooms]);

  const onSubmit = async (data) => {
    try {
      setError(null);
      clearErrors();
      
      // Additional validation before submission
      if (!isValid) {
        setError('Please fix all validation errors before submitting');
        return;
      }
      
      // Check if selected room is still available
      const selectedRoom = availableRooms.find(room => room.id === data.room_id);
      if (!selectedRoom) {
        setError('Selected room is no longer available. Please select another room.');
        return;
      }
      
      // Check if patient is still eligible
      const selectedPatient = patients.find(patient => patient.id === data.patient_id);
      if (!selectedPatient) {
        setError('Selected patient is no longer available. Please select another patient.');
        return;
      }
      
      // Check if staff is still authorized
      const selectedStaff = staff.find(member => member.id === data.staff_id);
      if (!selectedStaff) {
        setError('Selected staff member is no longer available. Please select another staff member.');
        return;
      }
      
      const result = await createAdmission(data);
      if (onSuccess) {
        onSuccess(result);
      }
      else {        // Reset form after successful submission
        console.log('inside else', result);
        
      }
    } catch (err) {
      console.log('err', err.message);
      
      const errorMessage = err.message || 'Failed to create admission';
      setError(errorMessage);
    }
  };

  const selectedRoom = availableRooms.find(room => room.id === selectedRoomId);

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={3}>
          <PersonAddIcon color="primary" />
          <Typography variant="h5" component="h2">
            Admit Patient
          </Typography>
        </Box>

        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 2 }}
            action={
              <Button
                color="inherit"
                size="small"
                onClick={() => setError(null)}
              >
                Dismiss
              </Button>
            }
          >
            <Typography variant="body2" fontWeight="medium">
              Admission Failed
            </Typography>
            <Typography variant="body2">
              {error}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Please check your selections and try again. If the problem persists, contact support.
            </Typography>
          </Alert>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Controller
                name="patient_id"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.patient_id}>
                    <InputLabel>Patient</InputLabel>
                    <Select
                      {...field}
                      label="Patient"
                      startAdornment={<PersonIcon />}
                    >
                      {patients
                        .map((patient) => (
                          <MenuItem key={patient.id} value={patient.id}>
                            <Box display="flex" flexDirection="column">
                              <Typography variant="body1" fontWeight="medium">
                                {patient.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                DOB: {patient.dob}
                              </Typography>
                            </Box>
                          </MenuItem>
                        ))}
                    </Select>
                    {errors.patient_id && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        <Typography variant="caption">
                          {errors.patient_id.message}
                        </Typography>
                      </Alert>
                    )}
                  </FormControl>
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="room_id"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.room_id}>
                    <InputLabel>Room</InputLabel>
                    <Select
                      {...field}
                      label="Room"
                      startAdornment={<RoomIcon />}
                    >
                      {availableRooms.map((room) => (
                        <MenuItem key={room.id} value={room.id}>
                          <Box display="flex" flexDirection="column" width="100%">
                            <Box display="flex" justifyContent="space-between" alignItems="center">
                              <Typography variant="body1" fontWeight="medium">
                                Room {room.room_number}
                              </Typography>
                              <Typography variant="body2" color="primary" fontWeight="bold">
                                ${(room.daily_rate_cents / 100).toFixed(2)}/day
                              </Typography>
                            </Box>
                            <Typography variant="caption" color="text.secondary">
                              Type: {room.type.toUpperCase()} | Status: {room.status.toUpperCase()}
                            </Typography>
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                    {errors.room_id && (
                      <Typography variant="caption" color="error">
                        {errors.room_id.message}
                      </Typography>
                    )}
                  </FormControl>
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="staff_id"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.staff_id}>
                    <InputLabel>Staff Member</InputLabel>
                    <Select
                      {...field}
                      label="Staff Member"
                    >
                      {staff.map((member) => (
                        <MenuItem key={member.id} value={member.id}>
                          {member.name} ({member.role})
                        </MenuItem>
                      ))}
                    </Select>
                    {errors.staff_id && (
                      <Typography variant="caption" color="error">
                        {errors.staff_id.message}
                      </Typography>
                    )}
                  </FormControl>
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="admission_date"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Admission Date"
                    type="datetime-local"
                    error={!!errors.admission_date}
                    helperText={errors.admission_date?.message}
                    InputLabelProps={{
                      shrink: true,
                    }}
                  />
                )}
              />
            </Grid>

            {selectedRoom && (
              <Grid item xs={12}>
                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="h6" gutterBottom>
                    Selected Room Details
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Room Number:
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {selectedRoom.room_number}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Type:
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {selectedRoom.type.toUpperCase()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Daily Rate:
                      </Typography>
                      <Typography variant="body1" fontWeight="bold" color="primary">
                        ${(selectedRoom.daily_rate_cents / 100).toFixed(2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Status:
                      </Typography>
                      <Typography variant="body1" fontWeight="bold" color="success">
                        AVAILABLE
                      </Typography>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
            )}
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Box display="flex" gap={2} justifyContent="flex-end">
            <Button
              variant="outlined"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              startIcon={isSubmitting ? <CircularProgress size={20} /> : <SaveIcon />}
              disabled={isSubmitting || !isValid}
            >
              {isSubmitting ? 'Creating...' : 'Admit Patient'}
            </Button>
            {error && (
              <Button
                variant="outlined"
                onClick={() => {
                  setError(null);
                  // Refresh available rooms
                  fetchRooms({ available_only: true });
                }}
                sx={{ ml: 1 }}
              >
                Retry
              </Button>
            )}
          </Box>
        </form>
      </CardContent>
      

    </Card>
  );
};

export default AdmissionForm;
