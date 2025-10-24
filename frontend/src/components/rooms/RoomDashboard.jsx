import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  Button,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Hotel as RoomIcon,
  CheckCircle as AvailableIcon,
  Cancel as OccupiedIcon,
  Build as MaintenanceIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { useRoomContext } from '../../contexts/RoomContext';
import RoomList from './RoomList';
import RoomFilters from './RoomFilters';
import RoomSearch from './RoomSearch';

const RoomDashboard = () => {
  const { 
    rooms, 
    loading, 
    error, 
    fetchRooms, 
    getRoomStatistics 
  } = useRoomContext();
  
  const [filters, setFilters] = useState({
    type: null,
    status: null,
    available_only: false
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [statistics, setStatistics] = useState(null);

  const loadStatistics = useCallback(async () => {
    try {
      // This would call the backend statistics endpoint
      // For now, calculate from current rooms
      const stats = {
        total_rooms: rooms.length,
        available_rooms: rooms.filter(r => r.status === 'available').length,
        occupied_rooms: rooms.filter(r => r.status === 'occupied').length,
        maintenance_rooms: rooms.filter(r => r.status === 'maintenance').length,
        occupancy_rate: 0
      };
      
      if (stats.total_rooms > 0) {
        stats.occupancy_rate = (stats.occupied_rooms / stats.total_rooms) * 100;
      }
      
      setStatistics(stats);
    } catch (err) {
      console.error('Failed to load statistics:', err);
    }
  }, [rooms]);

  useEffect(() => {
    fetchRooms(filters);
  }, [filters.type, filters.status, filters.available_only]);

  useEffect(() => {
    loadStatistics();
  }, [rooms, loadStatistics]);

  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
  };

  const handleRefresh = () => {
    fetchRooms(filters);
    loadStatistics();
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'available':
        return <AvailableIcon color="success" />;
      case 'occupied':
        return <OccupiedIcon color="error" />;
      case 'maintenance':
        return <MaintenanceIcon color="warning" />;
      default:
        return <RoomIcon />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'available':
        return 'success';
      case 'occupied':
        return 'error';
      case 'maintenance':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (loading && !rooms.length) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Error loading rooms: {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Room Management Dashboard
        </Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Toggle Filters">
            <IconButton onClick={() => setShowFilters(!showFilters)}>
              <FilterIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Statistics Cards */}
      {statistics && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1}>
                  <RoomIcon color="primary" />
                  <Typography variant="h6">Total Rooms</Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {statistics.total_rooms}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1}>
                  <AvailableIcon color="success" />
                  <Typography variant="h6">Available</Typography>
                </Box>
                <Typography variant="h4" color="success.main">
                  {statistics.available_rooms}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1}>
                  <OccupiedIcon color="error" />
                  <Typography variant="h6">Occupied</Typography>
                </Box>
                <Typography variant="h4" color="error.main">
                  {statistics.occupied_rooms}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1}>
                  <MaintenanceIcon color="warning" />
                  <Typography variant="h6">Maintenance</Typography>
                </Box>
                <Typography variant="h4" color="warning.main">
                  {statistics.maintenance_rooms}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Occupancy Rate */}
      {statistics && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Occupancy Rate
          </Typography>
          <Box display="flex" alignItems="center" gap={2}>
            <Box flexGrow={1}>
              <Box
                sx={{
                  width: '100%',
                  height: 20,
                  backgroundColor: 'grey.200',
                  borderRadius: 1,
                  overflow: 'hidden'
                }}
              >
                <Box
                  sx={{
                    width: `${statistics.occupancy_rate}%`,
                    height: '100%',
                    backgroundColor: statistics.occupancy_rate > 80 ? 'error.main' : 
                                   statistics.occupancy_rate > 60 ? 'warning.main' : 'success.main',
                    transition: 'width 0.3s ease'
                  }}
                />
              </Box>
            </Box>
            <Typography variant="h6" fontWeight="bold">
              {statistics.occupancy_rate.toFixed(1)}%
            </Typography>
          </Box>
        </Paper>
      )}

      {/* Filters and Search */}
      {showFilters && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Filters & Search
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              <RoomFilters 
                filters={filters}
                onFilterChange={handleFilterChange}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <RoomSearch 
                searchTerm={searchTerm}
                onSearch={handleSearch}
              />
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Room List */}
      <RoomList 
        filters={filters}
        searchTerm={searchTerm}
        onRoomSelect={(room) => {
          console.log('Selected room:', room);
          // Handle room selection
        }}
      />
    </Box>
  );
};

export default RoomDashboard;
