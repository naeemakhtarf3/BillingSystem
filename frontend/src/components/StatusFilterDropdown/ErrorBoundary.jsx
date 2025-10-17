import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { ErrorOutline } from '@mui/icons-material';

/**
 * Error Boundary for StatusFilterDropdown Component
 * 
 * Catches and handles errors in the StatusFilterDropdown component,
 * providing a fallback UI and error recovery options.
 */
class StatusFilterDropdownErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details for debugging
    console.error('StatusFilterDropdown Error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <Paper 
          elevation={1}
          sx={{
            p: 3,
            textAlign: 'center',
            backgroundColor: '#ffebee',
            border: '1px solid #f44336',
            borderRadius: 2
          }}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <ErrorOutline 
              sx={{ 
                fontSize: 48, 
                color: '#f44336',
                mb: 2
              }} 
            />
            
            <Typography variant="h6" color="error" sx={{ mb: 1 }}>
              Filter Error
            </Typography>
            
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              The status filter encountered an error. You can still view all invoices.
            </Typography>
            
            <Button 
              variant="contained" 
              color="primary" 
              onClick={this.handleRetry}
              sx={{ mb: 1 }}
            >
              Try Again
            </Button>
            
            <Typography variant="caption" color="text.secondary">
              If the problem persists, please refresh the page.
            </Typography>
          </Box>
        </Paper>
      );
    }

    return this.props.children;
  }
}

export default StatusFilterDropdownErrorBoundary;
