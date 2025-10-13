# ADK + AG-UI + CopilotKit Integration for Clinic Billing System

This document describes the integration of Google's Agent Development Kit (ADK) with AG-UI Protocol and CopilotKit into your existing clinic billing system.

## 🚀 What's Been Added

### Backend Integration
- **ADK Agent**: A specialized AI agent for clinic billing operations
- **AG-UI Protocol**: Real-time communication bridge between frontend and backend
- **Custom Tools**: Patient search, billing summaries, recent activity tracking
- **Database Integration**: Direct access to your existing SQLite database

### Frontend Integration
- **CopilotKit UI**: Interactive AI assistant sidebar
- **Shared State**: Real-time synchronization between agent and UI
- **Generative UI**: Dynamic components for agent responses
- **Theme Customization**: AI-powered UI theming

## 🛠️ Installation

### Prerequisites
- Python 3.8+ with pip
- Node.js 16+ with npm
- Your existing clinic billing system

### Quick Setup
Run the setup script:
```bash
setup_copilotkit.bat
```

### Manual Setup

#### Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend Dependencies
```bash
cd frontend
npm install
```

## 🏃‍♂️ Running the System

### Start Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Access Points
- **Main Application**: http://localhost:5173
- **AI Assistant**: Available as sidebar in the main app
- **AG-UI Endpoint**: http://localhost:8000/ag-ui
- **API Documentation**: http://localhost:8000/docs

## 🤖 AI Agent Capabilities

The clinic billing agent can help with:

### Patient Management
- **Search Patients**: "Find patient John Smith"
- **Patient Details**: "Show me patient details for ID 123"
- **Patient Records**: Access to full patient information and history

### Billing Operations
- **Billing Summary**: "What's our billing summary?"
- **Revenue Tracking**: "Show me total revenue"
- **Outstanding Invoices**: "How much is outstanding?"
- **Payment History**: "Show recent payments"

### System Analytics
- **Recent Activity**: "Show me recent activity"
- **Performance Metrics**: "What's our clinic performance?"
- **Trend Analysis**: "Show payment trends"

### UI Customization
- **Theme Changes**: "Set the theme to blue"
- **Color Customization**: "Change colors to green"
- **Interface Updates**: Real-time UI modifications

### Additional Features
- **Weather Information**: "What's the weather in New York?"
- **General Assistance**: Help with any clinic-related questions

## 🔧 Technical Architecture

### Backend Components
```
backend/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── clinic_agent.py      # Main ADK agent
│   │   └── ag_ui_server.py      # AG-UI integration
│   ├── core/
│   │   └── config.py            # Updated with Google API key
│   └── main.py                  # Updated with AG-UI mount
```

### Frontend Components
```
frontend/src/
├── components/
│   ├── CopilotProvider.jsx      # CopilotKit provider
│   ├── ClinicCopilotSidebar.jsx # AI assistant UI
│   └── Layout.jsx               # Updated with sidebar
└── App.jsx                      # Updated with provider
```

### Key Features
- **Real-time Communication**: AG-UI protocol enables instant frontend-backend sync
- **Database Integration**: Direct access to existing patient, invoice, and payment data
- **Custom Tools**: Specialized functions for clinic operations
- **Generative UI**: Dynamic components that render based on agent responses
- **Shared State**: Bidirectional state management between agent and frontend

## 🎯 Usage Examples

### Patient Search
```
User: "Find patient John Smith"
Agent: Uses search_patients tool → Returns matching patients
UI: Displays patient list with details
```

### Billing Summary
```
User: "What's our billing summary?"
Agent: Uses get_billing_summary tool → Returns revenue data
UI: Shows comprehensive billing overview
```

### Theme Customization
```
User: "Set the theme to green"
Agent: Uses set_theme_color tool → Updates theme
UI: Immediately applies new color scheme
```

## 🔐 Configuration

### Environment Variables
The system uses your existing `.env` file with the addition of:
```env
GOOGLE_API_KEY=AIzaSyDi0QD7_-N7JJFXm5B6wbhkXXJdnT_hKZo
```

### API Endpoints
- **Main API**: `/api/v1/*` (existing endpoints)
- **AG-UI**: `/ag-ui/*` (new agent communication)
- **Health Check**: `/health`

## 🐛 Troubleshooting

### Common Issues

1. **Agent Not Responding**
   - Check if backend is running on port 8000
   - Verify Google API key is set correctly
   - Check browser console for connection errors

2. **Database Connection Issues**
   - Ensure SQLite database exists in backend directory
   - Check database permissions
   - Verify models are properly imported

3. **Frontend Build Issues**
   - Run `npm install` to ensure all dependencies are installed
   - Check for version conflicts in package.json
   - Clear node_modules and reinstall if needed

### Debug Mode
Enable debug logging by setting:
```env
DEBUG=True
```

## 📚 Additional Resources

- [CopilotKit Documentation](https://docs.copilotkit.ai/)
- [AG-UI Protocol](https://github.com/CopilotKit/ag-ui)
- [Google ADK Documentation](https://developers.google.com/adk)
- [Original Integration Guide](https://www.copilotkit.ai/blog/build-a-frontend-for-your-adk-agents-with-ag-ui)

## 🎉 What's Next?

The integration is now complete! You can:

1. **Test the AI Assistant**: Try asking it various questions about your clinic data
2. **Customize Tools**: Add more specialized functions to the agent
3. **Enhance UI**: Create more generative UI components
4. **Extend Functionality**: Add more complex clinic operations

The AI assistant is now fully integrated into your clinic billing system and ready to help streamline your operations!
