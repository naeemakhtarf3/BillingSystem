import React from 'react';
import { AdmissionProvider } from '../../contexts/AdmissionContext';
import ActiveAdmissions from '../../components/admissions/ActiveAdmissions';

const ActiveAdmissionsPage = () => {
  return (
    <AdmissionProvider>
      <ActiveAdmissions />
    </AdmissionProvider>
  );
};

export default ActiveAdmissionsPage;
