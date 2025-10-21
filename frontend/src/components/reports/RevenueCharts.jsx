import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, CircularProgress } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { fetchRevenue } from '../../services/reportService';

const brandBlue = '#4A90E2';
const brandTeal = '#00BFA5';

export default function RevenueCharts({ startDate, endDate, granularity }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    fetchRevenue({ start_date: startDate, end_date: endDate, granularity })
      .then((res) => {
        if (!isMounted) return;
        setData(res.points || []);
      })
      .finally(() => isMounted && setLoading(false));
    return () => {
      isMounted = false;
    };
  }, [startDate, endDate, granularity]);

  return (
    <Card aria-label="Revenue chart">
      <CardContent>
        <Typography variant="h6" component="h2" gutterBottom>
          Revenue ({granularity})
        </Typography>
        {loading ? (
          <CircularProgress size={24} aria-label="Loading revenue" />
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data} role="img" aria-label="Revenue over time">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="totalRevenue" stroke={brandBlue} strokeWidth={2} dot={false} name="Total Revenue" />
              <Line type="monotone" dataKey="averagePayment" stroke={brandTeal} strokeWidth={2} dot={false} name="Average Payment" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}


