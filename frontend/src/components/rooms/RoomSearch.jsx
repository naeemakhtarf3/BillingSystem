import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  InputAdornment,
  IconButton,
  Typography,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  Hotel as RoomIcon,
  CheckCircle as AvailableIcon,
  Cancel as OccupiedIcon,
  Build as MaintenanceIcon
} from '@mui/icons-material';

const RoomSearch = ({ searchTerm, onSearch, rooms = [] }) => {
  const [localSearchTerm, setLocalSearchTerm] = useState(searchTerm);
  const [searchResults, setSearchResults] = useState([]);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    setLocalSearchTerm(searchTerm);
  }, [searchTerm]);

  useEffect(() => {
    if (localSearchTerm.trim()) {
      const results = rooms.filter(room => 
        room.room_number.toLowerCase().includes(localSearchTerm.toLowerCase()) ||
        room.type.toLowerCase().includes(localSearchTerm.toLowerCase()) ||
        room.status.toLowerCase().includes(localSearchTerm.toLowerCase())
      );
      setSearchResults(results);
    } else {
      setSearchResults([]);
    }
  }, [localSearchTerm, rooms]);

  const handleSearchChange = (event) => {
    const value = event.target.value;
    setLocalSearchTerm(value);
    setShowResults(value.trim().length > 0);
  };

  const handleSearchSubmit = () => {
    onSearch(localSearchTerm);
    setShowResults(false);
  };

  const handleClearSearch = () => {
    setLocalSearchTerm('');
    onSearch('');
    setShowResults(false);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearchSubmit();
    }
  };

  const handleResultClick = (room) => {
    onSearch(room.room_number);
    setShowResults(false);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'available':
        return <AvailableIcon color="success" fontSize="small" />;
      case 'occupied':
        return <OccupiedIcon color="error" fontSize="small" />;
      case 'maintenance':
        return <MaintenanceIcon color="warning" fontSize="small" />;
      default:
        return <RoomIcon fontSize="small" />;
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

  return (
    <Box position="relative">
      <Typography variant="h6" gutterBottom>
        Search Rooms
      </Typography>
      
      <TextField
        fullWidth
        placeholder="Search by room number, type, or status..."
        value={localSearchTerm}
        onChange={handleSearchChange}
        onKeyPress={handleKeyPress}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
          endAdornment: localSearchTerm && (
            <InputAdornment position="end">
              <IconButton
                aria-label="clear search"
                onClick={handleClearSearch}
                edge="end"
              >
                <ClearIcon />
              </IconButton>
            </InputAdornment>
          )
        }}
      />

      {/* Search Results Dropdown */}
      {showResults && searchResults.length > 0 && (
        <Paper
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            zIndex: 1000,
            maxHeight: 300,
            overflow: 'auto',
            mt: 1,
            boxShadow: 3
          }}
        >
          <List dense>
            {searchResults.map((room, index) => (
              <React.Fragment key={room.id}>
                <ListItem
                  button
                  onClick={() => handleResultClick(room)}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'action.hover'
                    }
                  }}
                >
                  <ListItemIcon>
                    {getStatusIcon(room.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body1" fontWeight="medium">
                          Room {room.room_number}
                        </Typography>
                        <Chip
                          label={room.type.toUpperCase()}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Chip
                          label={room.status.toUpperCase()}
                          size="small"
                          color={getStatusColor(room.status)}
                          variant="filled"
                        />
                        <Typography variant="caption" color="text.secondary">
                          ${(room.daily_rate_cents / 100).toFixed(2)}/day
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
                {index < searchResults.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}

      {/* No Results */}
      {showResults && searchResults.length === 0 && localSearchTerm.trim() && (
        <Paper
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            zIndex: 1000,
            mt: 1,
            p: 2,
            boxShadow: 3
          }}
        >
          <Typography variant="body2" color="text.secondary" textAlign="center">
            No rooms found matching "{localSearchTerm}"
          </Typography>
        </Paper>
      )}

      {/* Search Summary */}
      {searchTerm && (
        <Box mt={1}>
          <Typography variant="caption" color="text.secondary">
            Searching for: "{searchTerm}"
            {searchResults.length > 0 && ` (${searchResults.length} results)`}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default RoomSearch;
