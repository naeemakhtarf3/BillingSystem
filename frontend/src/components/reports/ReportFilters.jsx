import React from 'react';
import { Box, TextField, MenuItem } from '@mui/material';

export default function ReportFilters({ startDate, endDate, granularity, onChange }) {
  return (
    <Box display="flex" gap={2} alignItems="center" aria-label="Report filters">
      <TextField
        label="Start Date"
        type="date"
        value={startDate || ''}
        onChange={(e) => onChange({ startDate: e.target.value })}
        InputLabelProps={{ shrink: true }}
      />
      <TextField
        label="End Date"
        type="date"
        value={endDate || ''}
        onChange={(e) => onChange({ endDate: e.target.value })}
        InputLabelProps={{ shrink: true }}
      />
      <TextField
        select
        label="Granularity"
        value={granularity}
        onChange={(e) => onChange({ granularity: e.target.value })}
      >
        <MenuItem value="day">Day</MenuItem>
        <MenuItem value="week">Week</MenuItem>
        <MenuItem value="month">Month</MenuItem>
      </TextField>
    </Box>
  );
}


