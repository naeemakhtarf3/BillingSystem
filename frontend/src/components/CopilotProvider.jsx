import React from 'react';
import { CopilotKit } from '@copilotkit/react-core';

const CopilotProvider = ({ children }) => {
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  return (
    <CopilotKit
      runtimeUrl= {API_BASE_URL+"/agent/copilot"}
      // Optional: Add any additional configuration
    >
      {children}
    </CopilotKit>
  );
};

export default CopilotProvider;
