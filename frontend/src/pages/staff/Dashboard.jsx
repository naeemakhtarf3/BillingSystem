import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert
} from '@mui/material'
import {
  Receipt,
  Payment,
  People,
  TrendingUp
} from '@mui/icons-material'
import { api } from '../../services/api'

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalInvoices: 0,
    totalRevenue: 0,
    pendingPayments: 0,
    totalPatients: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch invoices
      const invoicesResponse = await api.get('/invoices')
      const invoices = invoicesResponse.data
      
      // Fetch patients
      const patientsResponse = await api.get('/patients')
      const patients = patientsResponse.data
      
      // Calculate stats
      const totalInvoices = invoices.length
      const totalRevenue = invoices
        .filter(inv => inv.status === 'paid')
        .reduce((sum, inv) => sum + inv.total_amount_cents, 0) / 100
      
      const pendingPayments = invoices
        .filter(inv => inv.status === 'issued').length
      
      const totalPatients = patients.length
      
      setStats({
        totalInvoices,
        totalRevenue,
        pendingPayments,
        totalPatients
      })
      
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const StatCard = ({ title, value, icon, color = 'primary' }) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="h2">
              {value}
            </Typography>
          </Box>
          <Box color={`${color}.main`}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  )

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Invoices"
            value={stats.totalInvoices}
            icon={<Receipt sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Revenue"
            value={`$${stats.totalRevenue.toFixed(2)}`}
            icon={<TrendingUp sx={{ fontSize: 40 }} />}
            color="secondary"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Payments"
            value={stats.pendingPayments}
            icon={<Payment sx={{ fontSize: 40 }} />}
            color="warning"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Patients"
            value={stats.totalPatients}
            icon={<People sx={{ fontSize: 40 }} />}
            color="info"
          />
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
