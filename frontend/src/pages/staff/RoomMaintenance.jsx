import React from 'react';
import { RoomProvider } from '../../contexts/RoomContext';
import RoomStatusManager from '../../components/rooms/RoomStatusManager';

const RoomMaintenance = () => {
  return (
    <RoomProvider>
      <RoomStatusManager />
    </RoomProvider>
  );
};

export default RoomMaintenance;
