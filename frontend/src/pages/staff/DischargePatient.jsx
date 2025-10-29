import React, { useState, useEffect } from 'react';
import { AdmissionProvider, useAdmissionContext } from '../../contexts/AdmissionContext';
import DischargeForm from '../../components/admissions/DischargeForm';
import { 
  Box, 
  Paper, 
  Typography, 
  Alert, 
  Card, 
  CardContent, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  TablePagination, 
  Button, 
  Chip, 
  CircularProgress,
  Avatar,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment,
  Grid
} from '@mui/material';
import {
  Person as PersonIcon,
  Hotel as RoomIcon,
  AccessTime as TimeIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  PersonRemove as DischargeIcon
} from '@mui/icons-material';

// Component for displaying the list of discharged admissions
const DischargePatientList = ({ onSelectAdmission }) => {
  const { 
    loading, 
    error, 
    fetchDischargedAdmissions 
  } = useAdmissionContext();
  
  const [dischargedAdmissions, setDischargedAdmissions] = useState([]);
  
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadDischargedAdmissions();
  }, []);

  const loadDischargedAdmissions = async () => {
    try {
      const response = await fetchDischargedAdmissions();
      // Handle both array response and object with admissions array
      const admissionsArray = Array.isArray(response) ? response : (response.admissions || []);
      setDischargedAdmissions(admissionsArray);
    } catch (err) {
      console.error('Failed to load discharged admissions:', err);
      setDischargedAdmissions([]);
    }
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

  const filteredAdmissions = dischargedAdmissions.filter(admission => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      admission.patient?.name?.toLowerCase().includes(searchLower) ||
      admission.patient_id?.toString().includes(searchLower) ||
      admission.room?.room_number?.toLowerCase().includes(searchLower) ||
      admission.id?.toString().includes(searchLower)
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
        Error loading discharged admissions: {error}
      </Alert>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6" gutterBottom>
            Discharged Patients ({filteredAdmissions.length})
          </Typography>
          <Box display="flex" gap={1}>
            <Tooltip title="Refresh">
              <IconButton onClick={loadDischargedAdmissions} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <TextField
          fullWidth
          placeholder="Search discharged patients by name, ID, or room number..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 2 }}
        />

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Patient</TableCell>
                <TableCell>Room</TableCell>
                <TableCell>Admission Date</TableCell>
                <TableCell>Discharge Date</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
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
                        {admission.discharge_date ? formatDate(admission.discharge_date) : 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <TimeIcon fontSize="small" />
                        <Typography variant="body2">
                          {admission.discharge_date ? formatDuration(admission.admission_date) : 'N/A'}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={admission.status.toUpperCase()}
                        color="default"
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<PersonIcon />}
                        onClick={() => onSelectAdmission(admission)}
                        color="primary"
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
          count={filteredAdmissions.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </CardContent>
    </Card>
  );
};

const DischargePatient = () => {
  const [selectedAdmission, setSelectedAdmission] = useState(null);

  const handleSelectAdmission = (admission) => {
    setSelectedAdmission(admission);
  };

  const handleDischargeSuccess = (result) => {
    console.log('Patient discharged successfully:', result);
    setSelectedAdmission(null);
  };

  const handleDischargeCancel = () => {
    console.log('Discharge cancelled');
    setSelectedAdmission(null);
  };

  return (
    <AdmissionProvider>
      <Box>
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Discharged Patients
          </Typography>
          <Typography variant="body1" color="text.secondary">
            View discharged patients and their discharge details below.
          </Typography>
        </Paper>
        
        {!selectedAdmission ? (
          <DischargePatientList onSelectAdmission={handleSelectAdmission} />
        ) : (
          <DischargeForm 
            admission={selectedAdmission}
            onSuccess={handleDischargeSuccess}
            onCancel={handleDischargeCancel}
          />
        )}
      </Box>
    </AdmissionProvider>
  );
};

export default DischargePatient;
