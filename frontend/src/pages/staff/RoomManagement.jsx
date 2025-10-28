import React from 'react';
import { RoomProvider } from '../../contexts/RoomContext';
import RoomList from '../../components/rooms/RoomList';
import RoomDashboard from '../../components/rooms/RoomDashboard';
import { Box, Grid } from '@mui/material';

const RoomManagement = () => {
  return (
    <RoomProvider>
      <Box>
        <Grid container spacing={3}>
          {/* Room Dashboard */}
          <Grid item xs={12}>
            <RoomDashboard />
          </Grid>
        </Grid>
      </Box>
    </RoomProvider>
  );
};

export default RoomManagement;
