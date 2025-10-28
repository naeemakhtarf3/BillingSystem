import React, { useState } from 'react';
import { RoomProvider } from '../../contexts/RoomContext';
import { AdmissionProvider } from '../../contexts/AdmissionContext';
import AdmissionForm from '../../components/admissions/AdmissionForm';
import { Alert, Box, Paper, Snackbar, Typography } from '@mui/material';

const AdmitPatient = () => {
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' })

  return (
    <RoomProvider>
      <AdmissionProvider>
        <Box>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Admit New Patient
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Complete the form below to admit a new patient to the facility.
            </Typography>
          </Paper>
          
          <AdmissionForm 
            onSuccess={(admission) => {
              console.log('Patient admitted successfully:', admission);
              // You can add success notification here
              setSnackbar({ open: true, message: 'Patient admitted successfully', severity: 'success' })
            }}
            onCancel={() => {
              console.log('Admission cancelled');
              // You can add navigation back to dashboard here
            }}
          />
          <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar(s => ({ ...s, open: false }))}>
            <Alert onClose={() => setSnackbar(s => ({ ...s, open: false }))} severity={snackbar.severity} sx={{ width: '100%' }}>
              {snackbar.message}
            </Alert>
          </Snackbar>

        </Box>
      </AdmissionProvider>
    </RoomProvider>
  );
};

export default AdmitPatient;
