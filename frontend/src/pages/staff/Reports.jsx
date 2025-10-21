import React, { useState } from 'react';
import { Container, Box, Typography } from '@mui/material';
import ReportFilters from '../../components/reports/ReportFilters';
import RevenueCharts from '../../components/reports/RevenueCharts';
import OutstandingPayments from '../../components/reports/OutstandingPayments';

const Reports = () => {
  const [filters, setFilters] = useState({ granularity: 'month', startDate: '', endDate: '' });

  const handleChange = (partial) => setFilters((f) => ({ ...f, ...partial }));

  return (
    <Container maxWidth="lg">
      <Box my={3} aria-label="Reports Dashboard">
        <Typography variant="h4" component="h1" gutterBottom>
          Reports Dashboard
        </Typography>
        <ReportFilters
          startDate={filters.startDate}
          endDate={filters.endDate}
          granularity={filters.granularity}
          onChange={handleChange}
        />
        <Box mt={3}>
          <RevenueCharts
            startDate={filters.startDate}
            endDate={filters.endDate}
            granularity={filters.granularity}
          />
        </Box>
        <Box mt={3}>
          <OutstandingPayments />
        </Box>
      </Box>
    </Container>
  );
};

export default Reports;


