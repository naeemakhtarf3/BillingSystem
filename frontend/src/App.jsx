import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import CopilotProvider from './components/CopilotProvider'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import Login from './pages/staff/Login'
import Dashboard from './pages/staff/Dashboard'
import Patients from './pages/staff/Patients'
import PatientDetail from './pages/staff/patient/PatientDetail'
import Invoices from './pages/staff/Invoices'
import Payments from './pages/staff/Payments'
import Audit from './pages/staff/Audit'
import Reports from './pages/staff/Reports'
import PatientInvoiceView from './pages/patient/InvoiceView'
import PaymentSuccess from './pages/patient/PaymentSuccess'
import PaymentCancelled from './pages/patient/PaymentCancelled'
import SimpleAITest from './components/SimpleAITest'
import SimpleAIChat from './components/SimpleAIChat'

function App() {
  return (
    <ErrorBoundary>
      <CopilotProvider>
        <AuthProvider>
          <Routes>
          {/* Staff Routes */}
          <Route path="/staff/login" element={<Login />} />
          <Route path="/staff" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Navigate to="/staff/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="patients" element={<Patients />} />
            <Route path="patients/:id" element={<PatientDetail />} />
          <Route path="invoices" element={<Invoices />} />
          <Route path="payments" element={<Payments />} />
          <Route path="audit" element={<Audit />} />
          <Route path="reports" element={<Reports />} />
          <Route path="ai-test" element={<SimpleAITest />} />
          <Route path="ai-chat" element={<SimpleAIChat />} />
          </Route>

          {/* Patient Routes - These must come before catch-all */}
          <Route path="/patient/invoice/:invoiceId" element={
            <ProtectedRoute>
              <PatientInvoiceView />
            </ProtectedRoute>
          } />
          <Route path="/patient/payment/success" element={<PaymentSuccess />} />
          <Route path="/patient/payment/cancelled" element={<PaymentCancelled />} />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/staff/login" replace />} />
          
          {/* Catch-all route for any unmatched paths - must be last */}
          <Route path="*" element={<Navigate to="/staff/login" replace />} />
          </Routes>
        </AuthProvider>
      </CopilotProvider>
    </ErrorBoundary>
  )
}

export default App
