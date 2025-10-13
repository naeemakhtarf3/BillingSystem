import React from 'react'
import { Box, Typography, Card, CardContent } from '@mui/material'

const PaymentCancelled = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Payment Cancelled
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Payment cancelled page will be implemented here.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}

export default PaymentCancelled
