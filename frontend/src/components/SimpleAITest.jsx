import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper } from '@mui/material';

const SimpleAITest = () => {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!message.trim()) return;
    
    setLoading(true);
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

      const res = await fetch(API_BASE_URL+'/agent/chat/any', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [{ role: 'user', content: message }]
        })
      });
      
      const data = await res.json();
      setResponse(data.message || 'No response received');
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 600, margin: '0 auto' }}>
      <Typography variant="h4" gutterBottom>
        AI Assistant Test
      </Typography>
      
      <Paper sx={{ p: 2, mb: 2 }}>
        <TextField
          fullWidth
          label="Type your message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          disabled={loading}
          sx={{ mb: 2 }}
        />
        
        <Button
          variant="contained"
          onClick={sendMessage}
          disabled={loading || !message.trim()}
          fullWidth
        >
          {loading ? 'Sending...' : 'Send Message'}
        </Button>
      </Paper>

      {response && (
        <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
          <Typography variant="h6" gutterBottom>
            AI Response:
          </Typography>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {response}
          </Typography>
        </Paper>
      )}

      <Paper sx={{ p: 2, mt: 2, backgroundColor: '#e3f2fd' }}>
        <Typography variant="h6" gutterBottom>
          Try these commands:
        </Typography>
        <Typography variant="body2" component="div">
          • "Find patient John Smith"<br/>
          • "Show me the billing summary"<br/>
          • "Show recent activity"<br/>
          • "Set the theme to blue"<br/>
          • "Get weather in New York"
        </Typography>
      </Paper>
    </Box>
  );
};

export default SimpleAITest;
