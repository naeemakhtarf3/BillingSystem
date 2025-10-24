import React from 'react';
import { RoomProvider } from '../../contexts/RoomContext';
import { AdmissionProvider } from '../../contexts/AdmissionContext';
import AdmissionForm from '../../components/admissions/AdmissionForm';
import { Box, Paper, Typography } from '@mui/material';

const AdmitPatient = () => {
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
            }}
            onCancel={() => {
              console.log('Admission cancelled');
              // You can add navigation back to dashboard here
            }}
          />
        </Box>
      </AdmissionProvider>
    </RoomProvider>
  );
};

export default AdmitPatient;
