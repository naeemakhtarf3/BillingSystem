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
  Avatar
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
  CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { useAdmissionContext } from '../../contexts/AdmissionContext';
import AdmissionDetails from './AdmissionDetails';
import AdmissionSearch from './AdmissionSearch';

const ActiveAdmissions = () => {
  const { 
    activeAdmissions, 
    loading, 
    error, 
    fetchActiveAdmissions,
    getAdmissionStatistics,
    dischargePatient
  } = useAdmissionContext();
  
  const [statistics, setStatistics] = useState(null);
  const [selectedAdmission, setSelectedAdmission] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    fetchActiveAdmissions();
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      const stats = await getAdmissionStatistics();
      setStatistics(stats);
    } catch (err) {
      console.error('Failed to load statistics:', err);
    }
  };

  const handleRefresh = () => {
    fetchActiveAdmissions();
    loadStatistics();
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleAdmissionSelect = (admission) => {
    setSelectedAdmission(admission);
  };

  const handleDischargePatient = async (admission) => {
    console.log('inside handleDischargePatient parent', admission);
    
    try {
      // Call the discharge API with current date/time
      const dischargeData = {
        discharge_date: new Date().toISOString(),
        discharge_reason: 'recovery', // Default reason
        discharge_notes: 'Patient discharged from active admissions list'
      };
      
      const result = await dischargePatient(admission.id, dischargeData);
      console.log('Discharge successful:', result);
      
      // Refresh the active admissions list
      await fetchActiveAdmissions();
      
      // Show success message or redirect to discharge list
      alert('Patient discharged successfully!');
      
    } catch (error) {
      console.error('Discharge failed:', error);
      alert('Failed to discharge patient: ' + error.message);
    }
  };
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (admissionDate) => {
    const now = new Date();
    const admission = new Date(admissionDate);
    const diffMs = now - admission;
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

  if (loading && !activeAdmissions.length) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Error loading active admissions: {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Active Admissions
        </Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Toggle Filters">
            <IconButton onClick={() => setShowFilters(!showFilters)}>
              <FilterIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Statistics Cards */}
      {statistics && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1}>
                  <PeopleIcon color="primary" />
                  <Typography variant="h6">Active Admissions</Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {statistics.active_admissions}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1}>
                  <TrendingUpIcon color="success" />
                  <Typography variant="h6">Total Admissions</Typography>
                </Box>
                <Typography variant="h4" color="success.main">
                  {statistics.total_admissions}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1}>
                  <TimeIcon color="info" />
                  <Typography variant="h6">Avg. Length of Stay</Typography>
                </Box>
                <Typography variant="h4" color="info.main">
                  {statistics.average_length_of_stay_days?.toFixed(1)}d
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1}>
                  <CalendarIcon color="warning" />
                  <Typography variant="h6">Recent (7 days)</Typography>
                </Box>
                <Typography variant="h4" color="warning.main">
                  {statistics.recent_admissions_7_days}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Room Type Breakdown */}
      {statistics && statistics.room_type_breakdown && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Active Admissions by Room Type
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {Object.entries(statistics.room_type_breakdown).map(([type, count]) => (
              <Chip
                key={type}
                label={`${type.toUpperCase()}: ${count}`}
                color={getRoomTypeColor(type)}
                variant="outlined"
              />
            ))}
          </Box>
        </Paper>
      )}

      {/* Filters and Search */}
      {showFilters && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Filters & Search
          </Typography>
          <AdmissionSearch 
            onSearch={(filters) => {
              console.log('Search filters:', filters);
              // Implement search functionality
            }}
          />
        </Paper>
      )}

      {/* Admissions Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Active Admissions ({activeAdmissions.length})
          </Typography>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Patient</TableCell>
                  <TableCell>Room</TableCell>
                  <TableCell>Admission Date</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {activeAdmissions
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((admission) => (
                    <TableRow 
                      key={admission.id}
                      hover
                      onClick={() => handleAdmissionSelect(admission)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Avatar sx={{ width: 32, height: 32 }}>
                            <PersonIcon />
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              {admission.patient?.name || `Patient #${admission.patient_id}`}
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
                              Room {admission.room?.room_number || `Room #${admission.room_id}`}
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
                          {formatDuration(admission.admission_date)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={admission.status.toUpperCase()}
                          color={getStatusColor(admission.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAdmissionSelect(admission);
                          }}
                        >
                          View Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={activeAdmissions.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </CardContent>
      </Card>

      {/* Admission Details Dialog */}
      {selectedAdmission && (
        <AdmissionDetails
          admission={selectedAdmission}
          open={!!selectedAdmission}
          onClose={() => setSelectedAdmission(null)}
          handleDischargePatient={handleDischargePatient}
        />
      )}
    </Box>
  );
};

export default ActiveAdmissions;
