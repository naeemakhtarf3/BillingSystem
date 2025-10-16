import React from 'react'
import { Box, Typography, Button, Card, CardContent } from '@mui/material'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <Card sx={{ maxWidth: 500, width: '100%' }}>
            <CardContent>
              <Typography variant="h5" gutterBottom color="error">
                Something went wrong
              </Typography>
              <Typography variant="body1" sx={{ mb: 2 }}>
                We're sorry, but something unexpected happened. Please try refreshing the page.
              </Typography>
              <Button 
                variant="contained" 
                onClick={() => window.location.reload()}
                sx={{ mr: 2 }}
              >
                Refresh Page
              </Button>
              <Button 
                variant="outlined" 
                onClick={() => window.location.href = '/'}
              >
                Go Home
              </Button>
            </CardContent>
          </Card>
        </Box>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
