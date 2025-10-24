import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Chip,
  Box,
  IconButton,
  Tooltip,
  Button
} from '@mui/material';
import {
  Hotel as RoomIcon,
  Person as PersonIcon,
  Build as MaintenanceIcon,
  CheckCircle as AvailableIcon,
  Cancel as OccupiedIcon,
  Edit as EditIcon,
  Info as InfoIcon
} from '@mui/icons-material';

const RoomCard = ({ room, onRoomSelect, onEdit, showActions = true }) => {
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

  const getTypeColor = (type) => {
    switch (type) {
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

  const handleCardClick = () => {
    if (onRoomSelect) {
      onRoomSelect(room);
    }
  };

  const handleEditClick = (e) => {
    e.stopPropagation();
    if (onEdit) {
      onEdit(room);
    }
  };

  return (
    <Card 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        cursor: onRoomSelect ? 'pointer' : 'default',
        '&:hover': onRoomSelect ? {
          boxShadow: 3,
          transform: 'translateY(-2px)',
          transition: 'all 0.2s ease-in-out'
        } : {}
      }}
      onClick={handleCardClick}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <RoomIcon color="primary" />
            <Typography variant="h6" component="div" fontWeight="bold">
              {room.room_number}
            </Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            {getStatusIcon(room.status)}
            <Chip 
              label={room.status.toUpperCase()} 
              color={getStatusColor(room.status)}
              size="small"
            />
          </Box>
        </Box>

        <Box mb={2}>
          <Chip 
            label={room.type.toUpperCase()} 
            color={getTypeColor(room.type)}
            size="small"
            sx={{ mb: 1 }}
          />
        </Box>

        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="body2" color="text.secondary">
            Daily Rate:
          </Typography>
          <Typography variant="h6" color="primary" fontWeight="bold">
            {formatRate(room.daily_rate_cents)}
          </Typography>
        </Box>

        {room.status === 'available' && (
          <Box mt={2}>
            <Chip 
              label="READY FOR ADMISSION" 
              color="success" 
              size="small"
              sx={{ fontWeight: 'bold' }}
            />
          </Box>
        )}

        {room.status === 'occupied' && (
          <Box mt={2}>
            <Chip 
              label="OCCUPIED" 
              color="error" 
              size="small"
              sx={{ fontWeight: 'bold' }}
            />
          </Box>
        )}

        {room.status === 'maintenance' && (
          <Box mt={2}>
            <Chip 
              label="UNDER MAINTENANCE" 
              color="warning" 
              size="small"
              sx={{ fontWeight: 'bold' }}
            />
          </Box>
        )}
      </CardContent>

      {showActions && (
        <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
          <Tooltip title="View Details">
            <IconButton size="small" onClick={handleCardClick}>
              <InfoIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Edit Room">
            <IconButton size="small" onClick={handleEditClick}>
              <EditIcon />
            </IconButton>
          </Tooltip>
        </CardActions>
      )}
    </Card>
  );
};

export default RoomCard;
