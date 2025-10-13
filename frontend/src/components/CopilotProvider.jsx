import React from 'react';
import { CopilotKit } from '@copilotkit/react-core';

const CopilotProvider = ({ children }) => {
  return (
    <CopilotKit
      runtimeUrl="http://localhost:8000/agent/copilot"
      // Optional: Add any additional configuration
    >
      {children}
    </CopilotKit>
  );
};

export default CopilotProvider;
