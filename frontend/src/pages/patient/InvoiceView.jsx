import React, { useEffect, useState } from 'react'
import { Box, Typography, Card, CardContent, CircularProgress, Button, Table, TableBody, TableCell, TableHead, TableRow, Alert, Snackbar } from '@mui/material'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../../services/api'

const InvoiceView = () => {
  const { invoiceId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [invoice, setInvoice] = useState(null)
  const [error, setError] = useState('')
  const [paymentLoading, setPaymentLoading] = useState(false)
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' })

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const res = await api.get(`/invoices/${invoiceId}`)
        setInvoice(res.data)
      } catch (e) {
        console.error('Failed to load invoice', e)
        setError(e?.response?.data?.detail || e.message || 'Failed to load invoice')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [invoiceId])

  const handlePrint = () => {
    window.print()
  }

  const handleCompletePayment = async () => {
    setPaymentLoading(true)
    try {
      // Create payment link for this invoice using the public endpoint
      const response = await api.post(`/payments/invoices/${invoiceId}/create-payment-link-public`)
      
      if (response.data?.checkout_url) {
        // Redirect to Stripe checkout
        window.location.href = response.data.checkout_url
      } else {
        setSnackbar({ 
          open: true, 
          message: 'Failed to create payment link', 
          severity: 'error' 
        })
      }
    } catch (error) {
      console.error('Payment error:', error)
      setSnackbar({ 
        open: true, 
        message: error?.response?.data?.detail || 'Failed to process payment', 
        severity: 'error' 
      })
    } finally {
      setPaymentLoading(false)
    }
  }

  if (loading) return <CircularProgress />
  if (error) return <Typography color="error">{error}</Typography>
  if (!invoice) return <Typography>No invoice found</Typography>

  return (
    <Box sx={{ maxWidth: 900, margin: '0 auto', p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">Invoice {invoice.invoice_number}</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          {invoice.status === 'issued' || invoice.status === 'partially_paid' ? (
            <Button 
              variant="contained" 
              color="primary"
              onClick={handleCompletePayment}
              disabled={paymentLoading}
            >
              {paymentLoading ? 'Processing...' : 'Complete Payment'}
            </Button>
          ) : null}
          <Button variant="outlined" onClick={handlePrint}>Print / Download</Button>
        </Box>
      </Box>

      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="subtitle1">Patient: {invoice.patient_id}</Typography>
          <Typography variant="subtitle2">Status: {invoice.status}</Typography>
          <Typography variant="body2">Issued: {invoice.issued_at ? new Date(invoice.issued_at).toLocaleString() : '-'}</Typography>
          <Typography variant="body2">Due: {invoice.due_date || '-'}</Typography>

          <Table sx={{ mt: 2 }}>
            <TableHead>
              <TableRow>
                <TableCell>Description</TableCell>
                <TableCell>Qty</TableCell>
                <TableCell>Unit</TableCell>
                <TableCell>Tax</TableCell>
                <TableCell>Line Total</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {invoice.items && invoice.items.map((it) => (
                <TableRow key={it.id}>
                  <TableCell>{it.description}</TableCell>
                  <TableCell>{it.quantity}</TableCell>
                  <TableCell>{(it.unit_price_cents / 100).toFixed(2)} {invoice.currency}</TableCell>
                  <TableCell>{(it.tax_cents / 100).toFixed(2)} {invoice.currency}</TableCell>
                  <TableCell>{((it.quantity * it.unit_price_cents + it.tax_cents) / 100).toFixed(2)} {invoice.currency}</TableCell>
                </TableRow>
              ))}
              <TableRow>
                <TableCell colSpan={4} align="right"><strong>Total</strong></TableCell>
                <TableCell><strong>{(invoice.total_amount_cents / 100).toFixed(2)} {invoice.currency}</strong></TableCell>
              </TableRow>
            </TableBody>
          </Table>
          <Box sx={{ mt: 3 }}>
            <Button variant="contained" onClick={() => navigate('/staff/invoices')}>
              View Invoices
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert 
          severity={snackbar.severity} 
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default InvoiceView
