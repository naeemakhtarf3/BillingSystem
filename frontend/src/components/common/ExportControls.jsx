import React from 'react';
import { Button } from '@mui/material';

export default function ExportControls({ onExport, disabled, label = 'Download PDF' }) {
  return (
    <Button
      variant="contained"
      color="primary"
      onClick={onExport}
      disabled={disabled}
      aria-label={label}
      sx={{ backgroundColor: '#4A90E2', '&:hover': { backgroundColor: '#3a78bf' } }}
    >
      {label}
    </Button>
  );
}


