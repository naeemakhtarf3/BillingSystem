import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Grid,
  CircularProgress,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Button
} from '@mui/material';
import {
  Person as PersonIcon,
  Hotel as RoomIcon,
  AccessTime as TimeIcon,
  CheckCircle as ActiveIcon,
  Cancel as DischargedIcon,
  Visibility as ViewIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import { useAdmissionContext } from '../../contexts/AdmissionContext';

const AdmissionList = ({ filters = {}, onAdmissionSelect, showActions = true }) => {
  const { admissions, loading, error, fetchAdmissions } = useAdmissionContext();
  const [filteredAdmissions, setFilteredAdmissions] = useState([]);

  useEffect(() => {
    fetchAdmissions(filters);
  }, [filters]);

  useEffect(() => {
    setFilteredAdmissions(admissions);
  }, [admissions]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <ActiveIcon color="success" />;
      case 'discharged':
        return <DischargedIcon color="error" />;
      default:
        return <PersonIcon />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'discharged':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const calculateDuration = (admissionDate, dischargeDate) => {
    const start = new Date(admissionDate);
    const end = dischargeDate ? new Date(dischargeDate) : new Date();
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const handleAdmissionClick = (admission) => {
    if (onAdmissionSelect) {
      onAdmissionSelect(admission);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Error loading admissions: {error}
      </Alert>
    );
  }

  if (filteredAdmissions.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No admissions found matching your criteria
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Admissions ({filteredAdmissions.length})
      </Typography>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Patient</TableCell>
              <TableCell>Room</TableCell>
              <TableCell>Admission Date</TableCell>
              <TableCell>Discharge Date</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Status</TableCell>
              {showActions && <TableCell>Actions</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredAdmissions.map((admission) => (
              <TableRow 
                key={admission.id} 
                hover
                onClick={() => handleAdmissionClick(admission)}
                sx={{ cursor: 'pointer' }}
              >
                <TableCell>
                  <Box display="flex" alignItems="center" gap={1}>
                    <PersonIcon />
                    <Typography variant="subtitle1" fontWeight="medium">
                      Patient #{admission.patient_id}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center" gap={1}>
                    <RoomIcon />
                    <Typography variant="body2">
                      Room #{admission.room_id}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center" gap={1}>
                    <TimeIcon />
                    <Typography variant="body2">
                      {formatDate(admission.admission_date)}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {admission.discharge_date ? formatDate(admission.discharge_date) : 'N/A'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {calculateDuration(admission.admission_date, admission.discharge_date)} days
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center" gap={1}>
                    {getStatusIcon(admission.status)}
                    <Chip 
                      label={admission.status.toUpperCase()} 
                      color={getStatusColor(admission.status)}
                      size="small"
                    />
                  </Box>
                </TableCell>
                {showActions && (
                  <TableCell>
                    <Box display="flex" gap={1}>
                      <Tooltip title="View Details">
                        <IconButton 
                          size="small" 
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAdmissionClick(admission);
                          }}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      {admission.status === 'active' && (
                        <Tooltip title="Discharge Patient">
                          <IconButton 
                            size="small" 
                            onClick={(e) => {
                              e.stopPropagation();
                              // TODO: Handle discharge
                            }}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default AdmissionList;
