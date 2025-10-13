import React, { useEffect, useState } from 'react'
import { Box, Typography, Card, CardContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Snackbar, Alert, TextField } from '@mui/material'
import api from '../../services/api'

const Audit = () => {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' })
  const [filter, setFilter] = useState('')

  useEffect(() => {
    loadLogs()
  }, [])

  async function loadLogs() {
    setLoading(true)
    try {
      const res = await api.get('/audit')
      setLogs(res.data || [])
    } catch (err) {
      console.error(err)
      setSnackbar({ open: true, message: 'Failed to load audit logs', severity: 'error' })
    } finally {
      setLoading(false)
    }
  }

  function applyFilter() {
    // basic filter by action or target_type
    if (!filter) return loadLogs()
    const filtered = logs.filter(l => (l.action && l.action.includes(filter)) || (l.target_type && l.target_type.includes(filter)))
    setLogs(filtered)
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Audit Logs
      </Typography>

      <Card>
        <CardContent>
          <Typography variant="body2" gutterBottom>
            Recent audit logs (admin only).
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField label="Filter (action or target)" value={filter} onChange={(e) => setFilter(e.target.value)} size="small" />
            <Button variant="contained" onClick={applyFilter}>Apply</Button>
            <Button onClick={loadLogs}>Refresh</Button>
          </Box>

          <TableContainer component={Paper} sx={{ mt: 2 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Time</TableCell>
                  <TableCell>Actor</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>Target</TableCell>
                  <TableCell>Details</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {logs.map((l) => (
                  <TableRow key={l.id}>
                    <TableCell>{new Date(l.created_at).toLocaleString()}</TableCell>
                    <TableCell>{l.actor_type} {l.actor_id ? `(${l.actor_id})` : ''}</TableCell>
                    <TableCell>{l.action}</TableCell>
                    <TableCell>{l.target_type} {l.target_id ? `(${l.target_id})` : ''}</TableCell>
                    <TableCell><pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(l.details)}</pre></TableCell>
                  </TableRow>
                ))}
                {logs.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} align="center">{loading ? 'Loading...' : 'No logs found'}</TableCell>
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
    </Box>
  )
}

export default Audit
