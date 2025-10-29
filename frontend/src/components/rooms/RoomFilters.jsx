import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Chip,
  Button,
  Grid,
  Typography
} from '@mui/material';
import {
  Clear as ClearIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';

const RoomFilters = ({ filters, onFilterChange }) => {
  const handleTypeChange = (event) => {
    onFilterChange({ type: event.target.value || null });
  };

  const handleStatusChange = (event) => {
    onFilterChange({ status: event.target.value || null });
  };

  const handleAvailableOnlyChange = (event) => {
    onFilterChange({ available_only: event.target.checked });
  };

  const handleClearFilters = () => {
    onFilterChange({
      type: null,
      status: null,
      available_only: false
    });
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.type) count++;
    if (filters.status) count++;
    if (filters.available_only) count++;
    return count;
  };

  const activeFiltersCount = getActiveFiltersCount();

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={1} mb={2}>
        <FilterIcon />
        <Typography variant="h6">
          Room Filters
        </Typography>
        {activeFiltersCount > 0 && (
          <Chip 
            label={`${activeFiltersCount} active`} 
            color="primary" 
            size="small" 
          />
        )}
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={4}>
          <FormControl fullWidth>
            <InputLabel>Room Type</InputLabel>
            <Select
              value={filters.type || ''}
              onChange={handleTypeChange}
              label="Room Type"
            >
              <MenuItem value="">
                <em>All Types</em>
              </MenuItem>
              <MenuItem value="standard">Standard</MenuItem>
              <MenuItem value="private">Private</MenuItem>
              <MenuItem value="icu">ICU</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <FormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status || ''}
              onChange={handleStatusChange}
              label="Status"
            >
              <MenuItem value="">
                <em>All Statuses</em>
              </MenuItem>
              <MenuItem value="available">Available</MenuItem>
              <MenuItem value="occupied">Occupied</MenuItem>
              <MenuItem value="maintenance">Maintenance</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Box display="flex" alignItems="center" height="56px">
            <FormControlLabel
              control={
                <Checkbox
                  checked={filters.available_only}
                  onChange={handleAvailableOnlyChange}
                />
              }
              label="Available Only"
            />
          </Box>
        </Grid>
      </Grid>

      {/* Active Filters Display */}
      {activeFiltersCount > 0 && (
        <Box mt={2}>
          <Typography variant="subtitle2" gutterBottom>
            Active Filters:
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {filters.type && (
              <Chip
                label={`Type: ${filters.type}`}
                onDelete={() => onFilterChange({ type: null })}
                color="primary"
                variant="outlined"
              />
            )}
            {filters.status && (
              <Chip
                label={`Status: ${filters.status}`}
                onDelete={() => onFilterChange({ status: null })}
                color="primary"
                variant="outlined"
              />
            )}
            {filters.available_only && (
              <Chip
                label="Available Only"
                onDelete={() => onFilterChange({ available_only: false })}
                color="primary"
                variant="outlined"
              />
            )}
          </Box>
        </Box>
      )}

      {/* Clear Filters Button */}
      {activeFiltersCount > 0 && (
        <Box mt={2}>
          <Button
            variant="outlined"
            startIcon={<ClearIcon />}
            onClick={handleClearFilters}
            size="small"
          >
            Clear All Filters
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default RoomFilters;
