import React, { useState } from 'react';
import { 
  Fab, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  IconButton,
  Box
} from '@mui/material';
import { SmartToy, Close } from '@mui/icons-material';
import SimpleAIChat from './SimpleAIChat';

const FloatingAIAssistant = () => {
  const [open, setOpen] = useState(false);

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <>
      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="AI Assistant"
        onClick={handleOpen}
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 1000,
          backgroundColor: '#1976d2',
          '&:hover': {
            backgroundColor: '#1565c0',
          }
        }}
      >
        <SmartToy />
      </Fab>

      {/* AI Chat Dialog */}
      <Dialog
        open={open}
        onClose={handleClose}
        maxWidth="md"
        fullWidth
        fullScreen
        sx={{
          '& .MuiDialog-paper': {
            margin: 0,
            maxHeight: '100vh',
            borderRadius: 0,
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          backgroundColor: '#1976d2',
          color: 'white',
          padding: '16px 24px'
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SmartToy />
            AI Assistant
          </Box>
          <IconButton
            onClick={handleClose}
            sx={{ color: 'white' }}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ padding: 0, height: 'calc(100vh - 64px)' }}>
          <SimpleAIChat />
        </DialogContent>
      </Dialog>
    </>
  );
};

export default FloatingAIAssistant;
