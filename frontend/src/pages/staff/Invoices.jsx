import React, { useEffect, useState } from 'react'
import {
  Box,
  Typography,
  Button,
  CircularProgress,
    Snackbar,
    Alert,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  MenuItem,
  Paper,
  TableContainer
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import { api } from '../../services/api'
import { useNavigate } from 'react-router-dom'
import StatusFilterDropdown from '../../components/StatusFilterDropdown'

const emptyItem = () => ({ description: '', quantity: 1, unit_price_cents: 0, tax_cents: 0 })

const Invoices = () => {
  const [invoices, setInvoices] = useState([])
  const [filteredInvoices, setFilteredInvoices] = useState([])
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState({ patient_id: '', currency: 'USD', due_date: '', items: [emptyItem()], payment_method: 'online' })
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' })
  const navigate = useNavigate()
  const [actionLoading, setActionLoading] = useState({})
  const [confirm, setConfirm] = useState({ open: false, action: null, invoiceId: null })

  const load = async () => {
    setLoading(true)
    try {
      const [invRes, patRes] = await Promise.all([api.get('/invoices'), api.get('/patients')])
      const invoiceData = invRes.data || []
      setInvoices(invoiceData)
      setFilteredInvoices(invoiceData) // Initialize filtered invoices with all invoices
      setPatients(patRes.data || [])
    } catch (e) {
      console.error('Failed loading invoices or patients', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const patientMap = React.useMemo(() => {
    const m = {}
    patients.forEach((p) => { m[p.id] = p })
    return m
  }, [patients])

  // Transform invoices data for StatusFilterDropdown component
  const transformedInvoices = React.useMemo(() => {
    return invoices;
    return invoices.map(inv => ({
      id: inv.id,
      invoiceNumber: inv.invoice_number,
      patient: patientMap[inv.patient_id]?.name || patientMap[inv.patient_id]?.email || inv.patient_id,
      status: inv.status === 'draft' ? 'issued' : inv.status, // Map draft to issued for filtering
      originalStatus: inv.status, // Keep original status for action buttons
      amount: (inv.total_amount_cents / 100),
      issuedDate: inv.issued_at || inv.created_at,
      currency: inv.currency
    })).filter(inv => inv.id && inv.invoiceNumber) // Filter out invalid entries
  }, [invoices, patientMap])

  // Handle filter changes from StatusFilterDropdown
  const handleFilterChange = (filtered) => {
    console.log('Filter changed, filtered invoices:', filtered);
    setFilteredInvoices(filtered)
  }

  const openCreate = () => {
    setForm({ patient_id: patients[0]?.id || '', currency: 'USD', due_date: '', items: [emptyItem()] })
    setDialogOpen(true)
  }

  const updateItem = (idx, key, value) => {
    setForm((f) => {
      const items = [...f.items]
      items[idx] = { ...items[idx], [key]: value }
      return { ...f, items }
    })
  }

  const addItem = () => setForm((f) => ({ ...f, items: [...f.items, emptyItem()] }))
  const removeItem = (idx) => setForm((f) => ({ ...f, items: f.items.filter((_, i) => i !== idx) }))

  const createInvoice = async () => {
    setCreating(true)
    try {
      // Basic validation
      if (!form.patient_id) {
        setSnackbar({ open: true, message: 'Please select a patient', severity: 'error' })
        setCreating(false)
        return
      }
      for (const it of form.items) {
        if (!it.description || Number(it.unit_price_cents) <= 0) {
          setSnackbar({ open: true, message: 'Each item needs a description and a positive unit price', severity: 'error' })
          setCreating(false)
          return
        }
      }
      // Convert unit_price and tax fields to cents (assume user enters decimals)
      const payload = {
        patient_id: form.patient_id,
        currency: form.currency,
        due_date: form.due_date || null,
        payment_method: form.payment_method,
        items: form.items.map((it) => ({
          description: it.description,
          quantity: Number(it.quantity) || 1,
          unit_price_cents: Math.round(Number(it.unit_price_cents) * 100) || 0,
          tax_cents: Math.round(Number(it.tax_cents) * 100) || 0
        }))
      }

      const res = await api.post('/invoices', payload)
      const invoiceId = res.data.id
      //console.error('form.payment_method: ', form.payment_method)
      // If payment_method is online, create/send payment link (mock sending email)
      if (form.payment_method === 'online') {
        try {
          // send link and open it so patient/staff can complete payment
          const sendRes = await api.post(`/payments/invoices/${invoiceId}/send-payment-link`, { email: 'naeem.akhtar@f3technologies.eu' })
          console.log('sendRes: ', sendRes)
          const checkoutUrl = sendRes?.data?.checkout_url._url || sendRes?.checkout_url
          if (checkoutUrl) {
            // open the checkout URL (Stripe checkout or local backend page)
            window.open(checkoutUrl, '_blank')
            setSnackbar({ open: true, message: `Payment link opened (sent to ${sendRes.data?.sent_to || sendRes.sent_to})`, severity: 'success' })
          } else {
            setSnackbar({ open: true, message: `Payment link created but no URL returned`, severity: 'warning' })
          }
        } catch (sendErr) {
          console.error('Failed to send payment link', sendErr)
          setSnackbar({ open: true, message: 'Failed to send payment link', severity: 'error' })
        }
      } else {
        setSnackbar({ open: true, message: 'Invoice created (pay in cash)', severity: 'success' })
      }

      setDialogOpen(false)
      load()
      navigate(`/patient/invoice/${invoiceId}`)
    } catch (e) {
      console.error('Failed create invoice', e)
      // show error to user later
    } finally {
      setCreating(false)
    }
  }

  const issueInvoice = async (id) => {
    try {
    } catch (e) {
      console.error('Failed to issue invoice', e)
    }
    setActionLoading((s) => ({ ...s, [id + '_issue']: true }))
    try {
      await api.post(`/invoices/${id}/issue`)
      load()
      setSnackbar({ open: true, message: 'Invoice issued', severity: 'success' })
    } catch (e) {
      console.error('Failed to issue invoice', e)
      setSnackbar({ open: true, message: 'Failed to issue invoice', severity: 'error' })
    } finally {
      setActionLoading((s) => ({ ...s, [id + '_issue']: false }))
    }
  }

  const cancelInvoice = async (id) => {
    try {
    } catch (e) {
      console.error('Failed to cancel invoice', e)
    }
    setActionLoading((s) => ({ ...s, [id + '_cancel']: true }))
    try {
      await api.post(`/invoices/${id}/cancel`)
      load()
      setSnackbar({ open: true, message: 'Invoice cancelled', severity: 'success' })
    } catch (e) {
      console.error('Failed to cancel invoice', e)
      setSnackbar({ open: true, message: 'Failed to cancel invoice', severity: 'error' })
    } finally {
      setActionLoading((s) => ({ ...s, [id + '_cancel']: false }))
    }
  }

  if (loading) return <CircularProgress />

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom>Invoice Management</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="subtitle1">Filter by Status:</Typography>
          <StatusFilterDropdown
            invoices={transformedInvoices}
            onFilterChange={handleFilterChange}
            showNoResultsMessage={false} // We'll handle empty state in the table
          />
          <Button startIcon={<AddIcon />} variant="contained" onClick={openCreate}>Create Invoice</Button>
        </Box>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Invoice #</TableCell>
              <TableCell>Patient</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Issued</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredInvoices.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No invoices match the selected filter.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredInvoices.map((inv) => (
                <TableRow key={inv.id}>
                  <TableCell>{inv.invoice_number}</TableCell>
                  <TableCell>{patientMap[inv.patient_id]?.name || patientMap[inv.patient_id]?.email || inv.patient_id}</TableCell>
                  <TableCell>{inv.status}</TableCell>
                  <TableCell>{(inv.total_amount_cents / 100).toFixed(2)} {inv.currency}</TableCell>
                  <TableCell>{inv.issued_at ? new Date(inv.issued_at).toLocaleString() : '-'}</TableCell>
                  <TableCell>
                    <Button size="small" onClick={() => navigate(`/patient/invoice/${inv.id}`)}>View</Button>
                    {inv.status === 'draft' && (
                      <Button size="small" onClick={() => setConfirm({ open: true, action: 'issue', invoiceId: inv.id })} disabled={actionLoading[inv.id + '_issue']}>{actionLoading[inv.id + '_issue'] ? 'Issuing...' : 'Issue'}</Button>
                    )}
                    {inv.status !== 'paid' && inv.status !== 'cancelled' && inv.status !== 'draft' && (
                      <Button size="small" onClick={() => setConfirm({ open: true, action: 'cancel', invoiceId: inv.id })} disabled={actionLoading[inv.id + '_cancel']}>{actionLoading[inv.id + '_cancel'] ? 'Cancelling...' : 'Cancel'}</Button>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar((s) => ({ ...s, open: false }))}>
        <Alert severity={snackbar.severity} onClose={() => setSnackbar((s) => ({ ...s, open: false }))}>{snackbar.message}</Alert>
      </Snackbar>
      <Dialog open={confirm.open} onClose={() => setConfirm({ open: false, action: null, invoiceId: null })}>
        <DialogTitle>Confirm</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to {confirm.action} this invoice?</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirm({ open: false, action: null, invoiceId: null })}>No</Button>
          <Button onClick={async () => {
            const { action, invoiceId } = confirm
            setConfirm({ open: false, action: null, invoiceId: null })
            if (action === 'issue') await issueInvoice(invoiceId)
            if (action === 'cancel') await cancelInvoice(invoiceId)
          }} variant="contained">Yes</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Invoice</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
            <TextField select label="Patient" value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} fullWidth>
              {patients.map((p) => (
                <MenuItem key={p.id} value={p.id}>{p.name || p.email || p.id}</MenuItem>
              ))}
            </TextField>
            <TextField label="Currency" value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })} sx={{ width: 140 }} />
            <TextField label="Due date" type="date" InputLabelProps={{ shrink: true }} value={form.due_date || ''} onChange={(e) => setForm({ ...form, due_date: e.target.value })} sx={{ width: 200 }} />
            <TextField select label="Payment" value={form.payment_method} onChange={(e) => setForm({ ...form, payment_method: e.target.value })} sx={{ width: 180 }}>
              <MenuItem value="online">Pay Online (send link)</MenuItem>
              <MenuItem value="cash">Pay in Cash</MenuItem>
            </TextField>
          </Box>

          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1">Items</Typography>
            {form.items.map((it, idx) => (
              <Box key={idx} sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <TextField label="Description" value={it.description} onChange={(e) => updateItem(idx, 'description', e.target.value)} fullWidth />
                <TextField label="Qty" type="number" value={it.quantity} onChange={(e) => updateItem(idx, 'quantity', e.target.value)} sx={{ width: 100 }} />
                <TextField label="Unit (decimal)" value={it.unit_price_cents} onChange={(e) => updateItem(idx, 'unit_price_cents', e.target.value)} sx={{ width: 140 }} helperText="Enter major units (e.g. 12.50)" />
                <TextField label="Tax (decimal)" value={it.tax_cents} onChange={(e) => updateItem(idx, 'tax_cents', e.target.value)} sx={{ width: 140 }} helperText="Enter major units" />
                <IconButton onClick={() => removeItem(idx)}><DeleteIcon /></IconButton>
              </Box>
            ))}
            <Box sx={{ mt: 1 }}>
              <Button onClick={addItem}>Add Item</Button>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={createInvoice} disabled={creating}>{creating ? 'Creating...' : 'Create'}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Invoices
