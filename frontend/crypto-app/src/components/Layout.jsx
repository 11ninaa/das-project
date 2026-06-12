import React from 'react';
import { Link, useLocation } from 'react-router-dom';

/**
 * Main layout component that provides consistent navigation, active route highlighting,
 * and wraps page content with uniform styling.
 */
const Layout = ({ children }) => {
  const location = useLocation();

  /**
   * Navigation items configuration
   * Defines the main navigation links displayed in the header
   */
  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/search', label: 'Search' },
    { path: '/history', label: 'Historical Data' },
    { path: '/analysis', label: 'Technical Analysis' },
    { path: '/lstm', label: 'LSTM Prediction' },
    { path: '/onchain-sentiment', label: 'On-Chain & Sentiment' },
    { path: '/help', label: 'Help' },
  ];

  return (
    <div className="min-h-screen bg-slate-900">
      <nav className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-xl font-bold text-white">
                Crypto Analyzer
              </Link>
            </div>
            <div className="flex space-x-4">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === item.path || location.pathname.startsWith(item.path + '/')
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">{children}</main>
    </div>
  );
};

export default Layout;

