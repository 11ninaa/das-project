import React from 'react';
import Layout from './Layout';

/**
 * RouteWrapper component that wraps child routes with the Layout component for consistent navigation and page structure.
 */
const RouteWrapper = ({ children }) => {
  return <Layout>{children}</Layout>;
};

export default RouteWrapper;

