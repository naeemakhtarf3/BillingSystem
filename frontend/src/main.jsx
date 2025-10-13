import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import App from './App.jsx'

// Create theme with healthcare-focused design
const theme = createTheme({
  palette: {
    primary: {
      main: '#4A90E2', // Soft blue
    },
    secondary: {
      main: '#00BFA5', // Teal green
    },
    error: {
      main: '#FF6B6B', // Red for errors
    },
    warning: {
      main: '#FFD700', // Yellow for warnings
    },
    background: {
      default: '#FFFFFF',
      paper: '#F4F6F8',
    },
    text: {
      primary: '#333333',
      secondary: '#666666',
    },
  },
  typography: {
    fontFamily: 'Inter, Roboto, sans-serif',
    h1: {
      fontSize: '24px',
      fontWeight: 700,
      lineHeight: 1.5,
    },
    h2: {
      fontSize: '18px',
      fontWeight: 600,
      lineHeight: 1.5,
    },
    body1: {
      fontSize: '14px',
      lineHeight: 1.5,
    },
    button: {
      fontSize: '14px',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          padding: '10px 20px',
          transition: 'all 0.3s ease',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
