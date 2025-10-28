import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  Button,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Avatar,
  TextField,
  InputAdornment
} from '@mui/material';
import {
  People as PeopleIcon,
  Hotel as RoomIcon,
  AccessTime as TimeIcon,
  TrendingUp as TrendingUpIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Search as SearchIcon,
  Person as PersonIcon,
  CalendarToday as CalendarIcon,
  Receipt as ReceiptIcon,
  PersonRemove as DischargeIcon
} from '@mui/icons-material';
import { AdmissionProvider, useAdmissionContext } from '../../contexts/AdmissionContext';

const DischargedPatients = () => {
  const { 
    fetchDischargedAdmissions,
    loading, 
    error
  } = useAdmissionContext();
  
  const [dischargedAdmissions, setDischargedAdmissions] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadDischargedAdmissions();
    loadStatistics();
  }, []);

  const loadDischargedAdmissions = async () => {
    try {
      const response = await fetchDischargedAdmissions();
      setDischargedAdmissions(response.admissions || response);
    } catch (err) {
      console.error('Failed to load discharged admissions:', err);
    }
  };

  const loadStatistics = async () => {
    try {
      // Calculate statistics from discharged admissions
      const totalDischarged = dischargedAdmissions.length;
      const totalRevenue = dischargedAdmissions.reduce((sum, admission) => {
        // This would come from billing data in a real implementation
        return sum + (admission.room?.daily_rate_cents || 0);
      }, 0);
      
      setStatistics({
        total_discharged: totalDischarged,
        total_revenue_cents: totalRevenue,
        average_stay_days: calculateAverageStayDays()
      });
    } catch (err) {
      console.error('Failed to load statistics:', err);
    }
  };

  const calculateAverageStayDays = () => {
    if (dischargedAdmissions.length === 0) return 0;
    
    const totalDays = dischargedAdmissions.reduce((sum, admission) => {
      if (admission.discharge_date && admission.admission_date) {
        const duration = new Date(admission.discharge_date) - new Date(admission.admission_date);
        return sum + (duration / (1000 * 60 * 60 * 24));
      }
      return sum;
    }, 0);
    
    return totalDays / dischargedAdmissions.length;
  };

  const handleRefresh = () => {
    loadDischargedAdmissions();
    loadStatistics();
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (admissionDate, dischargeDate) => {
    const admission = new Date(admissionDate);
    const discharge = new Date(dischargeDate);
    const diffMs = discharge - admission;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffDays > 0) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ${diffHours % 24}h`;
    }
    return `${diffHours}h`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'discharged':
        return 'default';
      default:
        return 'default';
    }
  };

  const getRoomTypeColor = (type) => {
    switch (type) {
      case 'icu':
        return 'error';
      case 'private':
        return 'warning';
      case 'standard':
        return 'primary';
      default:
        return 'default';
    }
  };

  const getDischargeReasonColor = (reason) => {
    switch (reason) {
      case 'recovery':
        return 'success';
      case 'transfer':
        return 'info';
      case 'patient_request':
        return 'warning';
      case 'medical_necessity':
        return 'error';
      case 'other':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatCurrency = (cents) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  // Filter admissions based on search term
  const filteredAdmissions = dischargedAdmissions.filter(admission => {
    const searchLower = searchTerm.toLowerCase();
    return (
      admission.patient_id.toLowerCase().includes(searchLower) ||
      admission.room?.room_number?.toLowerCase().includes(searchLower) ||
      admission.discharge_reason?.toLowerCase().includes(searchLower)
    );
  });

  if (loading && !dischargedAdmissions.length) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Error loading discharged patients: {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Discharged Patients
        </Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Statistics Cards */}
      {statistics && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1}>
                  <PeopleIcon color="primary" />
                  <Typography variant="h6">Total Discharged</Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {statistics.total_discharged}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1}>
                  <TrendingUpIcon color="success" />
                  <Typography variant="h6">Total Revenue</Typography>
                </Box>
                <Typography variant="h4" color="success.main">
                  {formatCurrency(statistics.total_revenue_cents)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1}>
                  <TimeIcon color="info" />
                  <Typography variant="h6">Avg. Stay Duration</Typography>
                </Box>
                <Typography variant="h4" color="info.main">
                  {statistics.average_stay_days?.toFixed(1)}d
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Search */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search by patient ID, room number, or discharge reason..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      {/* Discharged Patients Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Discharged Patients ({filteredAdmissions.length})
          </Typography>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Patient</TableCell>
                  <TableCell>Room</TableCell>
                  <TableCell>Admission Date</TableCell>
                  <TableCell>Discharge Date</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Discharge Reason</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Invoice</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredAdmissions
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((admission) => (
                    <TableRow key={admission.id} hover>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Avatar sx={{ width: 32, height: 32 }}>
                            <PersonIcon />
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              Patient #{admission.patient_id}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              ID: {admission.id}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <RoomIcon />
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              Room {admission.room?.room_number || 'Unknown'}
                            </Typography>
                            <Chip
                              label={admission.room?.type?.toUpperCase() || 'UNKNOWN'}
                              size="small"
                              color={getRoomTypeColor(admission.room?.type)}
                              variant="outlined"
                            />
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {formatDate(admission.admission_date)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {formatDate(admission.discharge_date)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {formatDuration(admission.admission_date, admission.discharge_date)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={admission.discharge_reason?.toUpperCase() || 'UNKNOWN'}
                          color={getDischargeReasonColor(admission.discharge_reason)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={admission.status.toUpperCase()}
                          color={getStatusColor(admission.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {admission.invoice_id ? (
                          <Button
                            size="small"
                            variant="outlined"
                            startIcon={<ReceiptIcon />}
                            onClick={() => {
                              // Navigate to invoice or open in new tab
                              window.open(`/invoices/${admission.invoice_id}`, '_blank');
                            }}
                          >
                            View Invoice
                          </Button>
                        ) : (
                          <Typography variant="caption" color="text.secondary">
                            No Invoice
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={filteredAdmissions.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </CardContent>
      </Card>
    </Box>
  );
};

const DischargedPatientsPage = () => {
  return (
    <AdmissionProvider>
      <DischargedPatients />
    </AdmissionProvider>
  );
};

export default DischargedPatientsPage;
