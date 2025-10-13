import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Box, Typography, Card, CardContent, Button, CircularProgress, Table, TableBody, TableRow, TableCell, TableHead, Collapse, IconButton, TableContainer, Paper } from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import { api } from '../../../services/api'

const PatientDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [patient, setPatient] = useState(null)
  const [loading, setLoading] = useState(true)
  const [invoices, setInvoices] = useState([])
  const [expandedInvoice, setExpandedInvoice] = useState(null)
  const [invoicesLoading, setInvoicesLoading] = useState(false)
  const [invoicesError, setInvoicesError] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        console.log('PatientDetail: fetching id=', id)
        // Try without trailing slash first, then try with trailing slash if not found
        let res
        try {
          res = await api.get(`/patients/${id}`)
        } catch (err) {
          console.warn('PatientDetail: first fetch failed, trying with trailing slash', err?.response?.status)
          // if server redirects or requires trailing slash, try that
          res = await api.get(`/patients/${id}/`)
        }
        setPatient(res.data)
      } catch (e) {
        console.error('PatientDetail load error:', e)
        // store the error object to render a helpful message
        setPatient(null)
        setError(e?.response?.data?.detail || e.message || 'Failed to load patient')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  useEffect(() => {
    const loadInvoices = async () => {
      if (!id) return
      setInvoicesLoading(true)
      setInvoicesError('')
      try {
        const res = await api.get('/invoices', { params: { patient_id: id } })
        setInvoices(res.data || [])
      } catch (e) {
        console.error('Failed to load invoices for patient', id, e)
        setInvoicesError(e?.response?.data?.detail || e.message || 'Failed to load invoices')
      } finally {
        setInvoicesLoading(false)
      }
    }
    loadInvoices()
  }, [id])

  if (loading) return <CircularProgress />
  if (!patient) return <Typography color="error">{error || 'Patient not found'}</Typography>

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Patient</Typography>
      <Card>
        <CardContent>
          <Typography variant="h6">{patient.name}</Typography>
          <Typography variant="body2">Email: {patient.email}</Typography>
          <Typography variant="body2">Phone: {patient.phone}</Typography>
          <Typography variant="body2">DOB: {patient.dob}</Typography>
        </CardContent>
      </Card>

      <Box sx={{ mt: 2 }}>
        <Typography variant="h5" gutterBottom>Invoices</Typography>
        {invoicesLoading ? (
          <CircularProgress />
        ) : invoicesError ? (
          <Typography color="error">{invoicesError}</Typography>
        ) : invoices.length === 0 ? (
          <Typography>No invoices found for this patient.</Typography>
        ) : (
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Invoice #</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Issued</TableCell>
                <TableCell>Due</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {invoices.map((inv) => (
                <React.Fragment key={inv.id}>
                  <TableRow>
                    <TableCell>
                      <IconButton size="small" onClick={() => setExpandedInvoice(expandedInvoice === inv.id ? null : inv.id)}>
                        <ExpandMoreIcon style={{ transform: expandedInvoice === inv.id ? 'rotate(180deg)' : 'rotate(0deg)', transition: '0.2s' }} />
                      </IconButton>
                      {inv.invoice_number}
                    </TableCell>
                    <TableCell>{inv.status}</TableCell>
                    <TableCell>{(inv.total_amount_cents / 100).toFixed(2)} {inv.currency}</TableCell>
                    <TableCell>{inv.issued_at ? new Date(inv.issued_at).toLocaleString() : '-'}</TableCell>
                    <TableCell>{inv.due_date || '-'}</TableCell>
                    <TableCell>
                      <Button size="small" onClick={() => navigate(`/patient/invoice/${inv.id}`)}>Open</Button>
                      <Button size="small" onClick={() => window.open(`/patient/invoice/${inv.id}`, '_blank')}>Print</Button>
                    </TableCell>
                  </TableRow>

                  <TableRow>
                    <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
                      <Collapse in={expandedInvoice === inv.id} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1 }}>
                          {inv.items && inv.items.length > 0 ? (
                            <TableContainer component={Paper} variant="outlined">
                              <Table size="small">
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
                                  {inv.items.map((it) => (
                                    <TableRow key={it.id}>
                                      <TableCell>{it.description}</TableCell>
                                      <TableCell>{it.quantity}</TableCell>
                                      <TableCell>{(it.unit_price_cents / 100).toFixed(2)} {inv.currency}</TableCell>
                                      <TableCell>{(it.tax_cents / 100).toFixed(2)} {inv.currency}</TableCell>
                                      <TableCell>{((it.quantity * it.unit_price_cents + it.tax_cents) / 100).toFixed(2)} {inv.currency}</TableCell>
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>
                            </TableContainer>
                          ) : (
                            <Typography variant="body2">No line items for this invoice.</Typography>
                          )}
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              ))}
            </TableBody>
          </Table>
        )}
      </Box>

      <Box sx={{ mt: 2 }}>
        <Button variant="outlined" onClick={() => navigate(-1)}>Back</Button>
      </Box>
    </Box>
  )
}

export default PatientDetail
