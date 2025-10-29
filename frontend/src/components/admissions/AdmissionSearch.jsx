import React, { useState } from 'react';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Grid,
  Typography,
  Chip,
  IconButton,
  InputAdornment
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  FilterList as FilterIcon,
  Sort as SortIcon
} from '@mui/icons-material';

const AdmissionSearch = ({ onSearch, onClear }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    roomType: '',
    sortBy: 'admission_date',
    sortOrder: 'desc'
  });

  const handleSearch = () => {
    const searchParams = {
      searchTerm: searchTerm.trim(),
      ...filters
    };
    onSearch(searchParams);
  };

  const handleClear = () => {
    setSearchTerm('');
    setFilters({
      status: '',
      roomType: '',
      sortBy: 'admission_date',
      sortOrder: 'desc'
    });
    if (onClear) {
      onClear();
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (searchTerm.trim()) count++;
    if (filters.status) count++;
    if (filters.roomType) count++;
    if (filters.sortBy !== 'admission_date') count++;
    if (filters.sortOrder !== 'desc') count++;
    return count;
  };

  const activeFiltersCount = getActiveFiltersCount();

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={1} mb={2}>
        <SearchIcon />
        <Typography variant="h6">
          Search & Filter Admissions
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
        {/* Search Term */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Search"
            placeholder="Search by patient ID, room number, or staff ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: searchTerm && (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="clear search"
                    onClick={() => setSearchTerm('')}
                    edge="end"
                  >
                    <ClearIcon />
                  </IconButton>
                </InputAdornment>
              )
            }}
          />
        </Grid>

        {/* Status Filter */}
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              label="Status"
            >
              <MenuItem value="">
                <em>All Statuses</em>
              </MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="discharged">Discharged</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {/* Room Type Filter */}
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Room Type</InputLabel>
            <Select
              value={filters.roomType}
              onChange={(e) => handleFilterChange('roomType', e.target.value)}
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

        {/* Sort By */}
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Sort By</InputLabel>
            <Select
              value={filters.sortBy}
              onChange={(e) => handleFilterChange('sortBy', e.target.value)}
              label="Sort By"
            >
              <MenuItem value="admission_date">Admission Date</MenuItem>
              <MenuItem value="patient_id">Patient ID</MenuItem>
              <MenuItem value="room_id">Room Number</MenuItem>
              <MenuItem value="staff_id">Staff ID</MenuItem>
              <MenuItem value="duration">Duration</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {/* Sort Order */}
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Order</InputLabel>
            <Select
              value={filters.sortOrder}
              onChange={(e) => handleFilterChange('sortOrder', e.target.value)}
              label="Order"
            >
              <MenuItem value="desc">Newest First</MenuItem>
              <MenuItem value="asc">Oldest First</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      {/* Active Filters Display */}
      {activeFiltersCount > 0 && (
        <Box mt={2}>
          <Typography variant="subtitle2" gutterBottom>
            Active Filters:
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {searchTerm && (
              <Chip
                label={`Search: "${searchTerm}"`}
                onDelete={() => setSearchTerm('')}
                color="primary"
                variant="outlined"
              />
            )}
            {filters.status && (
              <Chip
                label={`Status: ${filters.status}`}
                onDelete={() => handleFilterChange('status', '')}
                color="primary"
                variant="outlined"
              />
            )}
            {filters.roomType && (
              <Chip
                label={`Type: ${filters.roomType}`}
                onDelete={() => handleFilterChange('roomType', '')}
                color="primary"
                variant="outlined"
              />
            )}
            {filters.sortBy !== 'admission_date' && (
              <Chip
                label={`Sort: ${filters.sortBy}`}
                onDelete={() => handleFilterChange('sortBy', 'admission_date')}
                color="primary"
                variant="outlined"
              />
            )}
            {filters.sortOrder !== 'desc' && (
              <Chip
                label={`Order: ${filters.sortOrder}`}
                onDelete={() => handleFilterChange('sortOrder', 'desc')}
                color="primary"
                variant="outlined"
              />
            )}
          </Box>
        </Box>
      )}

      {/* Action Buttons */}
      <Box mt={3} display="flex" gap={2}>
        <Button
          variant="contained"
          startIcon={<SearchIcon />}
          onClick={handleSearch}
        >
          Search
        </Button>
        <Button
          variant="outlined"
          startIcon={<ClearIcon />}
          onClick={handleClear}
        >
          Clear All
        </Button>
      </Box>

      {/* Quick Filters */}
      <Box mt={3}>
        <Typography variant="subtitle2" gutterBottom>
          Quick Filters:
        </Typography>
        <Box display="flex" gap={1} flexWrap="wrap">
          <Button
            size="small"
            variant="outlined"
            onClick={() => {
              setFilters(prev => ({ ...prev, status: 'active' }));
              handleSearch();
            }}
          >
            Active Only
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={() => {
              setFilters(prev => ({ ...prev, roomType: 'icu' }));
              handleSearch();
            }}
          >
            ICU Only
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={() => {
              setFilters(prev => ({ 
                ...prev, 
                sortBy: 'duration',
                sortOrder: 'desc'
              }));
              handleSearch();
            }}
          >
            Longest Stay
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={() => {
              setFilters(prev => ({ 
                ...prev, 
                sortBy: 'admission_date',
                sortOrder: 'desc'
              }));
              handleSearch();
            }}
          >
            Most Recent
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default AdmissionSearch;
