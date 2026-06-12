import React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { getOHLCV } from '../../utils/ohlcvHelper';

/**
 * BarChart Component
 * 
 * Displays OHLCV data as a bar chart showing price ranges over time.
 * Each bar represents the high-low range, with open and close as markers.
 * 
 * @param {Array<Object>} data - Array of stock price objects with OHLCV data and date
 * @param {string} className - Additional CSS classes to apply to the chart container
 * @param {string} id - ID for the component (for export functionality)
 * @returns {JSX.Element} Bar chart component or empty state message
 */
const BarChart = ({ data, className = '', id = 'bar-chart' }) => {
  if (!data || data.length === 0) {
    return (
      <div id={id} className={`bg-slate-800 rounded-lg p-8 text-center ${className}`}>
        <p className="text-slate-400">No chart data available</p>
      </div>
    );
  }

  /**
   * Format data for bar chart visualization
   */
  const chartData = data.map((item) => {
    const ohlcv = getOHLCV(item);
    const open = parseFloat(ohlcv.open) || 0;
    const high = parseFloat(ohlcv.high) || 0;
    const low = parseFloat(ohlcv.low) || 0;
    const close = parseFloat(ohlcv.close) || 0;
    
    // Calculate range for visualization
    const range = high - low;
    const isUp = close >= open;
    
    return {
      date: item.date || '',
      open,
      high,
      low,
      close,
      range,
      isUp,
      // For stacked bars showing the range
      'High-Low Range': range,
      'Open Price': open,
      'Close Price': close,
    };
  });

  /**
   * Custom tooltip component
   */
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 shadow-xl">
          <p className="text-slate-300 font-semibold mb-2">{data.date}</p>
          <p className="text-green-400">High: ${data.high?.toFixed(2)}</p>
          <p className="text-red-400">Low: ${data.low?.toFixed(2)}</p>
          <p className="text-blue-400">Open: ${data.open?.toFixed(2)}</p>
          <p className="text-yellow-400">Close: ${data.close?.toFixed(2)}</p>
          <p className="text-slate-400 mt-2">Range: ${data.range?.toFixed(2)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div id={id} className={`bg-slate-800 rounded-lg p-6 ${className}`}>
      <h3 className="text-xl font-semibold text-white mb-4">OHLCV Bar Chart</h3>
      <ResponsiveContainer width="100%" height={400}>
        <RechartsBarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="date"
            stroke="#94a3b8"
            tick={{ fill: '#94a3b8' }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar
            dataKey="high"
            fill="#10b981"
            name="High"
            opacity={0.7}
          />
          <Bar
            dataKey="low"
            fill="#ef4444"
            name="Low"
            opacity={0.7}
          />
          <Bar
            dataKey="open"
            fill="#3b82f6"
            name="Open"
            opacity={0.6}
          />
          <Bar
            dataKey="close"
            fill="#eab308"
            name="Close"
            opacity={0.6}
          />
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default BarChart;

