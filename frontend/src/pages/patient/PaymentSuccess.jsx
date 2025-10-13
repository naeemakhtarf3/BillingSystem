import React, { useState, useEffect } from 'react'
import { Box, Typography, Card, CardContent, CircularProgress, Alert } from '@mui/material'
import { useSearchParams } from 'react-router-dom'
import { api } from '../../services/api'

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [paymentData, setPaymentData] = useState(null)

  useEffect(() => {
    const sessionId = searchParams.get('session_id')
    
    if (!sessionId) {
      setError('No session ID found in URL')
      setLoading(false)
      return
    }

    const verifyPayment = async () => {
      try {
        const response = await api.post('/payments/verify-payment-success', {
          session_id: sessionId
        })
        
        setPaymentData(response.data)
        setLoading(false)
      } catch (err) {
        console.error('Payment verification failed:', err)
        setError(err.response?.data?.detail || 'Payment verification failed')
        setLoading(false)
      }
    }

    verifyPayment()
  }, [searchParams])

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Box textAlign="center">
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Verifying your payment...
          </Typography>
        </Box>
      </Box>
    )
  }

  if (error) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom color="error">
          Payment Verification Failed
        </Typography>
        <Card>
          <CardContent>
            <Alert severity="error">
              {error}
            </Alert>
            <Typography variant="body1" sx={{ mt: 2 }}>
              Please contact support if you believe this is an error.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom color="success.main">
        Payment Successful!
      </Typography>
      <Card>
        <CardContent>
          <Alert severity="success" sx={{ mb: 2 }}>
            {paymentData?.message || 'Your payment has been processed successfully.'}
          </Alert>
          
          {paymentData && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Payment Details
              </Typography>
              <Typography variant="body1">
                <strong>Invoice Number:</strong> {paymentData.invoice_number}
              </Typography>
              <Typography variant="body1">
                <strong>Amount Paid:</strong> ${paymentData.amount_paid?.toFixed(2)} {paymentData.currency}
              </Typography>
              <Typography variant="body1">
                <strong>Status:</strong> {paymentData.status}
              </Typography>
            </Box>
          )}
          
          <Typography variant="body1" sx={{ mt: 3 }}>
            Thank you for your payment. You will receive a confirmation email shortly.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}

export default PaymentSuccess
