import React from 'react';
import { Box } from '@mui/material';

const AccessibilityWrapper = ({ 
  children, 
  role, 
  ariaLabel, 
  ariaDescribedBy, 
  ariaExpanded, 
  ariaControls,
  tabIndex,
  onKeyDown,
  ...props 
}) => {
  return (
    <Box
      role={role}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      aria-expanded={ariaExpanded}
      aria-controls={ariaControls}
      tabIndex={tabIndex}
      onKeyDown={onKeyDown}
      {...props}
    >
      {children}
    </Box>
  );
};

export default AccessibilityWrapper;
