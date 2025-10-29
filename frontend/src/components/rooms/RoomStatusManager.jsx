import React, { useState, useEffect } from 'react';
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
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Avatar
} from '@mui/material';
import {
  Build as MaintenanceIcon,
  Hotel as RoomIcon,
  CheckCircle as AvailableIcon,
  Cancel as OccupiedIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import { useRoomContext } from '../../contexts/RoomContext';
import MaintenanceForm from './MaintenanceForm';

const RoomStatusManager = () => {
  const { 
    rooms, 
    loading, 
    error, 
    fetchRooms,
    updateRoomStatus,
    getRoomStatistics 
  } = useRoomContext();
  
  const [statistics, setStatistics] = useState(null);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [showMaintenanceForm, setShowMaintenanceForm] = useState(false);
  const [showStatusDialog, setShowStatusDialog] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [maintenanceRooms, setMaintenanceRooms] = useState([]);

  useEffect(() => {
    fetchRooms();
    loadStatistics();
  }, []);

  useEffect(() => {
    setMaintenanceRooms(rooms.filter(room => room.status === 'maintenance'));
  }, [rooms]);

  const loadStatistics = async () => {
    try {
      const stats = getRoomStatistics();
      setStatistics(stats);
    } catch (err) {
      console.error('Failed to load statistics:', err);
    }
  };

  const handleRefresh = () => {
    fetchRooms();
    loadStatistics();
  };

  const handleStatusChange = (room, newStatus) => {
    setSelectedRoom(room);
    setNewStatus(newStatus);
    setShowStatusDialog(true);
  };

  const handleConfirmStatusChange = async () => {
    try {
      await updateRoomStatus(selectedRoom.id, newStatus);
      setShowStatusDialog(false);
      setSelectedRoom(null);
      setNewStatus('');
      handleRefresh();
    } catch (err) {
      console.error('Failed to update room status:', err);
    }
  };

  const handleScheduleMaintenance = (room) => {
    setSelectedRoom(room);
    setShowMaintenanceForm(true);
  };

  const handleCompleteMaintenance = async (room) => {
    try {
      await updateRoomStatus(room.id, 'available');
      handleRefresh();
    } catch (err) {
      console.error('Failed to complete maintenance:', err);
    }
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

  const getStatusActions = (room) => {
    const actions = [];
    
    if (room.status === 'available') {
      actions.push(
        <Button
          key="maintenance"
          size="small"
          variant="outlined"
          startIcon={<MaintenanceIcon />}
          onClick={() => handleScheduleMaintenance(room)}
        >
          Schedule Maintenance
        </Button>
      );
    }
    
    if (room.status === 'maintenance') {
      actions.push(
        <Button
          key="complete"
          size="small"
          variant="contained"
          color="success"
          onClick={() => handleCompleteMaintenance(room)}
        >
          Complete Maintenance
        </Button>
      );
    }
    
    return actions;
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
          Room Status Manager
        </Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
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

      {/* Maintenance Rooms Alert */}
      {maintenanceRooms.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body1">
            <strong>{maintenanceRooms.length} room(s) in maintenance:</strong> {maintenanceRooms.map(room => room.room_number).join(', ')}
          </Typography>
        </Alert>
      )}

      {/* Rooms Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Room Status Management
          </Typography>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Room</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Rate</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rooms.map((room) => (
                  <TableRow key={room.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Avatar sx={{ width: 32, height: 32 }}>
                          <RoomIcon />
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            Room {room.room_number}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            ID: {room.id}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={room.type.toUpperCase()}
                        color={room.type === 'icu' ? 'error' : room.type === 'private' ? 'warning' : 'primary'}
                        variant="outlined"
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
                      <Typography variant="body2">
                        ${(room.daily_rate_cents / 100).toFixed(2)}/day
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1} flexWrap="wrap">
                        {getStatusActions(room)}
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<EditIcon />}
                          onClick={() => handleStatusChange(room, room.status)}
                        >
                          Edit Status
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Status Change Dialog */}
      <Dialog 
        open={showStatusDialog} 
        onClose={() => setShowStatusDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Change Room Status
        </DialogTitle>
        <DialogContent>
          <Box mt={2}>
            <Typography variant="body1" gutterBottom>
              Change status for <strong>Room {selectedRoom?.room_number}</strong>
            </Typography>
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>New Status</InputLabel>
              <Select
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value)}
                label="New Status"
              >
                <MenuItem value="available">Available</MenuItem>
                <MenuItem value="occupied">Occupied</MenuItem>
                <MenuItem value="maintenance">Maintenance</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowStatusDialog(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleConfirmStatusChange}
            disabled={!newStatus || newStatus === selectedRoom?.status}
          >
            Update Status
          </Button>
        </DialogActions>
      </Dialog>

      {/* Maintenance Form Dialog */}
      {selectedRoom && (
        <MaintenanceForm
          room={selectedRoom}
          open={showMaintenanceForm}
          onClose={() => {
            setShowMaintenanceForm(false);
            setSelectedRoom(null);
          }}
          onSuccess={() => {
            setShowMaintenanceForm(false);
            setSelectedRoom(null);
            handleRefresh();
          }}
        />
      )}
    </Box>
  );
};

export default RoomStatusManager;
