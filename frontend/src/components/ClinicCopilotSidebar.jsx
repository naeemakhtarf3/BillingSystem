import React, { useState } from 'react';
import { CopilotSidebar } from '@copilotkit/react-ui';

// State type for the clinic billing agent
const AgentState = {
  themeColor: '#1976d2', // Default Material-UI primary color
  selectedPatient: null,
  billingSummary: null,
  recentActivity: []
};

const ClinicCopilotSidebar = () => {
  const [themeColor, setThemeColor] = useState('#1976d2');

  return (
    <div style={{ "--copilot-kit-primary-color": themeColor }}>
      <CopilotSidebar
        clickOutsideToClose={false}
        defaultOpen={true}
        labels={{
          title: "Clinic Billing Assistant",
          initial: `👋 Hi! I'm your Clinic Billing Assistant. I can help you with:

**Patient Management:**
- Search for patients by name or email
- View detailed patient information
- Manage patient records

**Billing Operations:**
- View billing summaries and revenue
- Check outstanding invoices
- Review recent payments

**System Analytics:**
- Get insights on clinic performance
- View recent activity
- Monitor payment trends

**UI Customization:**
- Change theme colors
- Customize the interface

Try asking me things like:
- "Find patient John Smith"
- "Show me the billing summary"
- "What's our recent activity?"
- "Set the theme to green"
- "Get weather in New York"

I'm here to help make your clinic billing management easier! 🏥`
        }}
      />
    </div>
  );
};

export default ClinicCopilotSidebar;
