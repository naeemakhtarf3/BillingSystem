import React from 'react';
import { Box, useMediaQuery, useTheme } from '@mui/material';

const ResponsiveContainer = ({ 
  children, 
  mobileProps = {}, 
  tabletProps = {}, 
  desktopProps = {},
  ...props 
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md'));
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'));

  const getResponsiveProps = () => {
    if (isMobile) return mobileProps;
    if (isTablet) return tabletProps;
    if (isDesktop) return desktopProps;
    return {};
  };

  return (
    <Box
      {...props}
      {...getResponsiveProps()}
    >
      {children}
    </Box>
  );
};

export default ResponsiveContainer;
