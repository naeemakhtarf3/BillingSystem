import React from 'react';
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Avatar
} from '@mui/material';
import {
  Person as PersonIcon,
  Hotel as RoomIcon,
  AccessTime as TimeIcon,
  CalendarToday as CalendarIcon,
  Receipt as ReceiptIcon,
  PersonRemove as DischargeIcon,
  Edit as EditIcon,
  Close as CloseIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  LocationOn as LocationIcon
} from '@mui/icons-material';

const AdmissionDetails = ({ admission, open, onClose }) => {
  if (!admission) return null;

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
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ${diffHours % 24} hours`;
    }
    return `${diffHours} hours`;
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

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <PersonIcon />
          <Typography variant="h6">
            Admission Details
          </Typography>
          <Box flexGrow={1} />
          <Chip
            label={admission.status.toUpperCase()}
            color={getStatusColor(admission.status)}
            size="small"
          />
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box>
          {/* Patient Information */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Patient Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <PersonIcon />
                    <Typography variant="body1">
                      <strong>Patient ID:</strong> {admission.patient_id}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <PhoneIcon />
                    <Typography variant="body1">
                      <strong>Contact:</strong> (555) 123-4567
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <EmailIcon />
                    <Typography variant="body1">
                      <strong>Email:</strong> patient{admission.patient_id}@example.com
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <LocationIcon />
                    <Typography variant="body1">
                      <strong>Address:</strong> 123 Main St, City, State
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Room Information */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Room Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <RoomIcon />
                    <Typography variant="body1">
                      <strong>Room Number:</strong> {admission.room?.room_number || 'Unknown'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip
                      label={admission.room?.type?.toUpperCase() || 'UNKNOWN'}
                      color={getRoomTypeColor(admission.room?.type)}
                      variant="outlined"
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body1">
                    <strong>Daily Rate:</strong> ${(admission.room?.daily_rate_cents || 0) / 100}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body1">
                    <strong>Status:</strong> 
                    <Chip
                      label={admission.room?.status?.toUpperCase() || 'UNKNOWN'}
                      color={admission.room?.status === 'occupied' ? 'error' : 'success'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Admission Timeline */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Admission Timeline
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <CalendarIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Admission Date"
                    secondary={formatDate(admission.admission_date)}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <TimeIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Duration of Stay"
                    secondary={formatDuration(admission.admission_date)}
                  />
                </ListItem>
                {admission.discharge_date && (
                  <ListItem>
                    <ListItemIcon>
                      <DischargeIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="Discharge Date"
                      secondary={formatDate(admission.discharge_date)}
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>

          {/* Staff Information */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Staff Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body1">
                    <strong>Admitting Staff ID:</strong> {admission.staff_id}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body1">
                    <strong>Staff Role:</strong> Doctor
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Billing Information */}
          {admission.invoice_id && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Billing Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <ReceiptIcon />
                      <Typography variant="body1">
                        <strong>Invoice ID:</strong> {admission.invoice_id}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body1">
                      <strong>Status:</strong> Pending
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Actions
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap">
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                disabled={admission.status !== 'active'}
              >
                Edit Admission
              </Button>
              <Button
                variant="contained"
                color="error"
                startIcon={<DischargeIcon />}
                disabled={admission.status !== 'active'}
              >
                Discharge Patient
              </Button>
              <Button
                variant="outlined"
                startIcon={<ReceiptIcon />}
                disabled={!admission.invoice_id}
              >
                View Invoice
              </Button>
            </Box>
          </Paper>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AdmissionDetails;
