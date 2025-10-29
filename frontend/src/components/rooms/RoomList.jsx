import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Grid,
  CircularProgress,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Hotel as RoomIcon,
  Person as PersonIcon,
  Build as MaintenanceIcon,
  CheckCircle as AvailableIcon,
  Cancel as OccupiedIcon
} from '@mui/icons-material';
import { useRoomContext } from '../../contexts/RoomContext';

const RoomList = ({ filters = {}, onRoomSelect }) => {
  const { rooms, loading, error } = useRoomContext();
  const [filteredRooms, setFilteredRooms] = useState([]);

  // Remove duplicate fetchRooms call - RoomDashboard already handles fetching
  // RoomList should only display rooms that are already fetched

  useEffect(() => {
    // Filter rooms based on the filters prop
    let filtered = rooms;
    
    if (filters.type) {
      filtered = filtered.filter(room => room.type?.toLowerCase() === filters.type?.toLowerCase());
    }
    
    if (filters.status) {
      filtered = filtered.filter(room => room.status?.toLowerCase() === filters.status?.toLowerCase());
    }
    
    if (filters.available_only) {
      filtered = filtered.filter(room => room.status?.toLowerCase() === 'available');
    }
    
    setFilteredRooms(filtered);
  }, [rooms, filters.type, filters.status, filters.available_only]);

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
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
    switch (status?.toLowerCase()) {
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

  const getTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'icu':
        return 'error';
      case 'private':
        return 'primary';
      case 'standard':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatRate = (cents) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const handleRoomClick = (room) => {
    if (onRoomSelect) {
      onRoomSelect(room);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
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

  if (filteredRooms.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No rooms found matching your criteria
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Rooms ({filteredRooms.length})
      </Typography>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Room</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Daily Rate</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredRooms.map((room) => (
              <TableRow 
                key={room.id} 
                hover
                onClick={() => handleRoomClick(room)}
                sx={{ cursor: 'pointer' }}
              >
                <TableCell>
                  <Box display="flex" alignItems="center" gap={1}>
                    <RoomIcon />
                    <Typography variant="subtitle1" fontWeight="medium">
                      {room.room_number}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={room.type.toUpperCase()} 
                    color={getTypeColor(room.type)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center" gap={1}>
                    {getStatusIcon(room.status)}
                    <Chip 
                      label={room.status.toUpperCase()} 
                      color={getStatusColor(room.status)}
                      size="small"
                    />
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {formatRate(room.daily_rate_cents)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton size="small" onClick={(e) => {
                      e.stopPropagation();
                      handleRoomClick(room);
                    }}>
                      <PersonIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default RoomList;
