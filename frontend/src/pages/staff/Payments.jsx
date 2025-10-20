import React, { useEffect, useState } from 'react'
import { Box, Typography, Card, CardContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Snackbar, Alert, Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@mui/material'
import api from '../../services/api'

const Payments = () => {
  const [payments, setPayments] = useState([])
  const [loading, setLoading] = useState(false)
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' })
  const [openNew, setOpenNew] = useState(false)
  const [newPayment, setNewPayment] = useState({ invoice_id: '', amount: '' })
 

  useEffect(() => {
    loadPayments()
  }, [])

  async function loadPayments() {
    setLoading(true)
    try {
      const res = await api.get('/payments')
      setPayments(res.data || [])
    } catch (err) {
      console.error(err)
      setSnackbar({ open: true, message: 'Failed to load payments', severity: 'error' })
    } finally {
      setLoading(false)
    }
  }

  function openNewDialog() {
    setNewPayment({ invoice_id: '', amount: '' })
    setOpenNew(true)
  }

  async function submitNewPayment() {
    if (!newPayment.invoice_id || !newPayment.amount) {
      setSnackbar({ open: true, message: 'Invoice and amount are required', severity: 'error' })
      return
    }

    try {
      const payload = {
        invoice_id: newPayment.invoice_id,
        amount_cents: Math.round(parseFloat(newPayment.amount) * 100),
        currency: 'USD',
        method: 'cash'
      }
      const res = await api.post('/payments', payload)
      const created = res.data
      setSnackbar({ open: true, message: 'Payment recorded', severity: 'success' })
      setOpenNew(false)
      // Optimistically add the created payment so invoice number appears immediately
      setPayments(prev => [
        {
          id: created.id,
          invoice_id: created.invoice_id,
          invoice_number: created.invoice_number,
          amount_cents: created.amount_cents,
          currency: created.currency,
          status: created.status,
          received_at: created.received_at
        },
        ...prev
      ])
      // no audit card shown after recording a payment
    } catch (err) {
      setSnackbar({ open: true, message: err?.response?.data?.detail || 'Failed to record payment', severity: 'error' })
    }
  }


  async function handleRefund(paymentId) {
    if (!confirm('Refund this payment? This cannot be undone.')) return
    try {
      await api.post(`/payments/${paymentId}/refund`)
      setSnackbar({ open: true, message: 'Refund processed', severity: 'success' })
      // Update local state
      setPayments(prev => prev.map(p => p.id === paymentId ? { ...p, status: 'REFUNDED' } : p))
    } catch (err) {
      console.error(err)
      setSnackbar({ open: true, message: err?.response?.data?.detail || 'Refund failed', severity: 'error' })
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Payment Management
      </Typography>

      <Card>
        <CardContent>
          {/* audit card intentionally hidden/UI will not fetch or show latest audit after recording a payment */}
          <Typography variant="body2" gutterBottom>
            Recent payments across invoices. Use the Refund action to process a refund (admin/billing roles only).
          </Typography>

          <Button variant="contained" sx={{ mb: 2 }} onClick={openNewDialog}>New Payment</Button>

          <TableContainer component={Paper} sx={{ mt: 2 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Payment ID</TableCell>
                  <TableCell>Invoice #</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Currency</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Received</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {payments.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell>{p.id}</TableCell>
                    <TableCell>{p.invoice_number}</TableCell>
                    <TableCell>{(p.amount_cents / 100).toFixed(2)}</TableCell>
                    <TableCell>{p.currency}</TableCell>
                    <TableCell>{p.status}</TableCell>
                    <TableCell>{p.received_at ? new Date(p.received_at).toLocaleString() : '-'}</TableCell>
                    <TableCell>
                      <Button size="small" variant="outlined" color="error" disabled={p.status && p.status.toUpperCase() !== 'SUCCEEDED' ? true : false} onClick={() => handleRefund(p.id)}>
                        Refund
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {payments.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center">{loading ? 'Loading payments...' : 'No payments found'}</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar(s => ({ ...s, open: false }))}>
        <Alert onClose={() => setSnackbar(s => ({ ...s, open: false }))} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>

      <Dialog open={openNew} onClose={() => setOpenNew(false)}>
        <DialogTitle>New Manual Payment</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Invoice ID" value={newPayment.invoice_id} onChange={(e) => setNewPayment(s => ({ ...s, invoice_id: e.target.value }))} sx={{ mt: 1 }} />
          <TextField fullWidth label="Amount (e.g. 123.45)" value={newPayment.amount} onChange={(e) => setNewPayment(s => ({ ...s, amount: e.target.value }))} sx={{ mt: 2 }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenNew(false)}>Cancel</Button>
          <Button variant="contained" onClick={submitNewPayment}>Record Payment</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Payments
