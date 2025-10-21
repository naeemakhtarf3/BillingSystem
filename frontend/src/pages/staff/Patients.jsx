import React, { useEffect, useState } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  CircularProgress,
  IconButton
} from '@mui/material'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import VisibilityIcon from '@mui/icons-material/Visibility'
import { useNavigate } from 'react-router-dom'
import { api } from '../../services/api'

const emptyForm = {
  name: '',
  email: '',
  phone: '',
  dob: '',
  patient_metadata: {}
}

const Patients = () => {
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [query, setQuery] = useState('')

  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [isEditing, setIsEditing] = useState(false)
  const [editingId, setEditingId] = useState(null)

  useEffect(() => {
    fetchPatients()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchPatients = async (q = '') => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/patients', { params: q ? { query: q } : {} })
      if(!res.data.error)
        setPatients(res.data || [])
      else
        setPatients([])
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to fetch patients')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    fetchPatients(query)
  }

  const openAdd = () => {
    setForm(emptyForm)
    setIsEditing(false)
    setEditingId(null)
    setDialogOpen(true)
  }

  const openEdit = (p) => {
    setForm({
      name: p.name || '',
      email: p.email || '',
      phone: p.phone || '',
      dob: p.dob ? p.dob.split('T')[0] : '',
      patient_metadata: p.patient_metadata || {}
    })
    setIsEditing(true)
    setEditingId(p.id)
    setDialogOpen(true)
  }

  const navigate = useNavigate()

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this patient?')) return
    setLoading(true)
    try {
      await api.delete(`/patients/${id}`)
      await fetchPatients()
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to delete patient')
    } finally {
      setLoading(false)
    }
  }

  const closeDialog = () => {
    setDialogOpen(false)
  }

  const handleChange = (field) => (e) => {
    const value = e.target.value
    setForm((s) => ({ ...s, [field]: value }))
  }

  const submitForm = async () => {
    setLoading(true)
    try {
      if (isEditing && editingId) {
        await api.put(`/patients/${editingId}`, {
          ...form,
          patient_metadata: form.patient_metadata || {}
        })
      } else {
        await api.post('/patients', {
          ...form,
          patient_metadata: form.patient_metadata || {}
        })
      }
      await fetchPatients()
      closeDialog()
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to save patient')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Patient Management
      </Typography>

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <form onSubmit={handleSearch}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={8} md={6}>
                <TextField
                  label="Search patients by name, email or phone"
                  fullWidth
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </Grid>
              <Grid item>
                <Button type="submit" variant="contained">
                  Search
                </Button>
              </Grid>
              <Grid item>
                <Button variant="outlined" onClick={openAdd}>
                  Add Patient
                </Button>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Card>
          <CardContent>
            {error && (
              <Typography color="error" sx={{ mb: 2 }}>
                {error}
              </Typography>
            )}

            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>DOB</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {patients.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell>{p.name}</TableCell>
                    <TableCell>{p.email}</TableCell>
                    <TableCell>{p.phone}</TableCell>
                    <TableCell>{p.dob ? p.dob.split('T')[0] : ''}</TableCell>
                    <TableCell>{new Date(p.created_at).toLocaleString()}</TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => { console.log('navigate to patient', p.id); navigate(`/staff/patients/${p.id}`) }}>
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton size="small" onClick={() => openEdit(p)}>
                        <EditIcon />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleDelete(p.id)}>
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      <Dialog open={dialogOpen} onClose={closeDialog} fullWidth maxWidth="sm">
        <DialogTitle>{isEditing ? 'Edit Patient' : 'Add Patient'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField label="Name" fullWidth value={form.name} onChange={handleChange('name')} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Email" fullWidth value={form.email} onChange={handleChange('email')} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Phone" fullWidth value={form.phone} onChange={handleChange('phone')} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Date of Birth" type="date" fullWidth value={form.dob} onChange={handleChange('dob')} InputLabelProps={{ shrink: true }} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDialog}>Cancel</Button>
          <Button onClick={submitForm} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Patients
