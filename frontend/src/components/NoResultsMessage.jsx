import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { SearchOff } from '@mui/icons-material';

/**
 * NoResultsMessage Component
 * 
 * Displays a user-friendly message when no invoices match the selected filter.
 * Provides clear feedback to help users understand why no data is displayed.
 * 
 * @param {Object} props - Component props
 * @param {string} [props.filterType='filter'] - Type of filter applied
 * @param {string} [props.message] - Custom message to display
 * @param {boolean} [props.showIcon=true] - Whether to show the search icon
 */
const NoResultsMessage = ({ 
  filterType = 'filter',
  message,
  showIcon = true 
}) => {
  const defaultMessage = `No invoices match the selected ${filterType}.`;
  const displayMessage = message || defaultMessage;

  return (
    <Paper 
      elevation={1}
      sx={{
        p: 4,
        textAlign: 'center',
        backgroundColor: '#f5f5f5',
        border: '1px solid #e0e0e0',
        borderRadius: 2,
        mt: 2
      }}
    >
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {showIcon && (
          <SearchOff 
            sx={{ 
              fontSize: 48, 
              color: '#9e9e9e',
              mb: 2
            }} 
          />
        )}
        
        <Typography 
          variant="h6" 
          color="text.secondary"
          sx={{ mb: 1 }}
        >
          No Results Found
        </Typography>
        
        <Typography 
          variant="body1" 
          color="text.secondary"
          sx={{ maxWidth: 400 }}
        >
          {displayMessage}
        </Typography>
        
        <Typography 
          variant="body2" 
          color="text.secondary"
          sx={{ mt: 2, fontStyle: 'italic' }}
        >
          Try selecting a different filter option or check back later.
        </Typography>
      </Box>
    </Paper>
  );
};

export default NoResultsMessage;
