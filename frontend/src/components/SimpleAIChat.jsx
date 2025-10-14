import React, { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  TextField, 
  IconButton, 
  Paper, 
  Typography, 
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider
} from '@mui/material';
import { Send as SendIcon, SmartToy as BotIcon, Person as PersonIcon } from '@mui/icons-material';

const SimpleAIChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your Clinic Billing Assistant. I can help you with patient management, billing summaries, and more. How can I assist you today?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/agent/chat/any', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [{ role: 'user', content: inputMessage }]
        })
      });

      const data = await response.json();
      
      const botMessage = {
        id: Date.now() + 1,
        text: data.message || 'No response received',
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: `Error: ${error.message}`,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <Box sx={{ 
      height: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      maxWidth: '800px',
      margin: '0 auto',
      border: '1px solid #e0e0e0',
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <Paper sx={{ 
        p: 2, 
        backgroundColor: '#1976d2', 
        color: 'white',
        borderRadius: 0
      }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BotIcon />
          Clinic Billing AI Assistant
        </Typography>
      </Paper>

      {/* Messages */}
      <Box sx={{ 
        flex: 1, 
        overflow: 'auto', 
        p: 2,
        backgroundColor: '#f5f5f5'
      }}>
        <List>
          {messages.map((message) => (
            <React.Fragment key={message.id}>
              <ListItem sx={{ 
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                alignItems: 'flex-start'
              }}>
                <Box sx={{ 
                  maxWidth: '70%',
                  display: 'flex',
                  flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                  alignItems: 'flex-start',
                  gap: 1
                }}>
                  <Avatar sx={{ 
                    backgroundColor: message.sender === 'user' ? '#1976d2' : '#4caf50',
                    width: 32,
                    height: 32
                  }}>
                    {message.sender === 'user' ? <PersonIcon /> : <BotIcon />}
                  </Avatar>
                  <Paper sx={{ 
                    p: 2,
                    backgroundColor: message.sender === 'user' ? '#1976d2' : 'white',
                    color: message.sender === 'user' ? 'white' : 'black',
                    borderRadius: '16px',
                    boxShadow: 1
                  }}>
                    <Typography variant="body1" sx={{ 
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word'
                    }}>
                      {message.text}
                    </Typography>
                    <Typography variant="caption" sx={{ 
                      display: 'block',
                      mt: 1,
                      opacity: 0.7,
                      fontSize: '0.75rem'
                    }}>
                      {formatTime(message.timestamp)}
                    </Typography>
                  </Paper>
                </Box>
              </ListItem>
              <Divider sx={{ my: 1 }} />
            </React.Fragment>
          ))}
          {isLoading && (
            <ListItem>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar sx={{ backgroundColor: '#4caf50', width: 32, height: 32 }}>
                  <BotIcon />
                </Avatar>
                <Paper sx={{ p: 2, backgroundColor: 'white' }}>
                  <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                    AI is thinking...
                  </Typography>
                </Paper>
              </Box>
            </ListItem>
          )}
          <div ref={messagesEndRef} />
        </List>
      </Box>

      {/* Input */}
      <Paper sx={{ 
        p: 2, 
        borderRadius: 0,
        borderTop: '1px solid #e0e0e0'
      }}>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Ask me about patients, billing, or anything else..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            variant="outlined"
            size="small"
          />
          <IconButton
            color="primary"
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            sx={{ 
              backgroundColor: '#1976d2',
              color: 'white',
              '&:hover': {
                backgroundColor: '#1565c0'
              },
              '&:disabled': {
                backgroundColor: '#e0e0e0',
                color: '#9e9e9e'
              }
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
        
        {/* Quick Actions */}
        <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {[
            "Show me the billing summary",
            "Find patient John Smith",
            "Find invoice CLINIC-202510-0038",
            "Show recent activity",
            "Set the theme to blue"
          ].map((suggestion) => (
            <Paper
              key={suggestion}
              sx={{
                p: 1,
                cursor: 'pointer',
                backgroundColor: '#f0f0f0',
                '&:hover': { backgroundColor: '#e0e0e0' },
                borderRadius: '16px'
              }}
              onClick={() => setInputMessage(suggestion)}
            >
              <Typography variant="caption" sx={{ fontSize: '0.75rem' }}>
                {suggestion}
              </Typography>
            </Paper>
          ))}
        </Box>
      </Paper>
    </Box>
  );
};

export default SimpleAIChat;
