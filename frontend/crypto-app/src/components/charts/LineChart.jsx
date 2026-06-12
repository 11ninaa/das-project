import React from 'react';
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { getOHLCV } from '../../utils/ohlcvHelper';

/**
 * LineChart Component
 * 
 * Displays OHLCV data as a line chart showing price trends over time.
 * Shows Open, High, Low, and Close prices as separate lines.
 * 
 * @param {Array<Object>} data - Array of stock price objects with OHLCV data and date
 * @param {string} className - Additional CSS classes to apply to the chart container
 * @param {string} id - ID for the component (for export functionality)
 * @returns {JSX.Element} Line chart component or empty state message
 */
const LineChart = ({ data, className = '', id = 'line-chart' }) => {
  if (!data || data.length === 0) {
    return (
      <div id={id} className={`bg-slate-800 rounded-lg p-8 text-center ${className}`}>
        <p className="text-slate-400">No chart data available</p>
      </div>
    );
  }

  /**
   * Format data for line chart visualization
   */
  const chartData = data.map((item) => {
    const ohlcv = getOHLCV(item);
    return {
      date: item.date || '',
      open: parseFloat(ohlcv.open) || 0,
      high: parseFloat(ohlcv.high) || 0,
      low: parseFloat(ohlcv.low) || 0,
      close: parseFloat(ohlcv.close) || 0,
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
        </div>
      );
    }
    return null;
  };

  return (
    <div id={id} className={`bg-slate-800 rounded-lg p-6 ${className}`}>
      <h3 className="text-xl font-semibold text-white mb-4">OHLCV Line Chart</h3>
      <ResponsiveContainer width="100%" height={400}>
        <RechartsLineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
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
          <Line
            type="monotone"
            dataKey="high"
            stroke="#10b981"
            strokeWidth={2}
            name="High"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="low"
            stroke="#ef4444"
            strokeWidth={2}
            name="Low"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="open"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Open"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="close"
            stroke="#eab308"
            strokeWidth={2}
            name="Close"
            dot={false}
          />
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LineChart;

