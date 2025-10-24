import React, { useState } from 'react';
import { AdmissionProvider } from '../../contexts/AdmissionContext';
import DischargeForm from '../../components/admissions/DischargeForm';
import { Box, Paper, Typography, Alert } from '@mui/material';

const DischargePatient = () => {
  const [selectedAdmission, setSelectedAdmission] = useState(null);

  // Mock admission data - in real app, this would come from API
  const mockAdmission = {
    id: 1,
    patient_id: 123,
    room_id: 1,
    admission_date: new Date().toISOString(),
    status: 'active',
    room: {
      id: 1,
      room_number: '101A',
      type: 'standard',
      daily_rate_cents: 15000
    }
  };

  return (
    <AdmissionProvider>
      <Box>
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Discharge Patient
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Select a patient to discharge and complete the discharge process.
          </Typography>
        </Paper>
        
        {!selectedAdmission ? (
          <Alert severity="info">
            <Typography variant="body1">
              Please select an active admission to discharge. 
              You can find active admissions in the "Active Admissions" section.
            </Typography>
          </Alert>
        ) : (
          <DischargeForm 
            admission={selectedAdmission}
            onSuccess={(result) => {
              console.log('Patient discharged successfully:', result);
              setSelectedAdmission(null);
            }}
            onCancel={() => {
              console.log('Discharge cancelled');
              setSelectedAdmission(null);
            }}
          />
        )}
      </Box>
    </AdmissionProvider>
  );
};

export default DischargePatient;
