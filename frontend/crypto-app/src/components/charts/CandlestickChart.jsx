import React from 'react';
import {
  ComposedChart,
  Line,
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
 * CandlestickChart Component
 * 
 * Displays OHLCV (Open, High, Low, Close, Volume) data as a candlestick-style chart.
 * Uses Recharts to visualize price movements over time with bars for high/low values
 * and lines for open/close prices. Includes interactive tooltips showing detailed OHLCV data.
 * 
 * @param {Array<Object>} data - Array of stock price objects with OHLCV data and date
 * @param {string} className - Additional CSS classes to apply to the chart container
 * @param {string} id - ID for the component (for export functionality)
 * @returns {JSX.Element} Candlestick chart component or empty state message
 */
const CandlestickChart = ({ data, className = '', id = 'candlestick-chart' }) => {
  if (!data || data.length === 0) {
    return (
      <div id={id} className={`bg-slate-800 rounded-lg p-8 text-center ${className}`}>
        <p className="text-slate-400">No chart data available</p>
      </div>
    );
  }

  /**
   * Format data for Recharts candlestick visualization
   * Extracts OHLCV values using the helper function and formats them for chart display
   * 
   * @returns {Array<Object>} Array of chart data points with date, open, high, low, close, volume
   */
  const chartData = data.map((item) => {
    const ohlcv = getOHLCV(item);
    return {
      date: item.date || '',
      open: parseFloat(ohlcv.open) || 0,
      high: parseFloat(ohlcv.high) || 0,
      low: parseFloat(ohlcv.low) || 0,
      close: parseFloat(ohlcv.close) || 0,
      volume: parseFloat(item.quote_volume) || 0,
    };
  });

  /**
   * Custom tooltip component for the chart
   * Displays detailed OHLCV information when hovering over chart data points
   * 
   * @param {boolean} active - Whether the tooltip is active (hovering)
   * @param {Array} payload - Array containing the data payload for the hovered point
   * @returns {JSX.Element|null} Tooltip component or null if not active
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
          <p className="text-slate-400 mt-2">Volume: {data.volume?.toLocaleString()}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div id={id} className={`bg-slate-800 rounded-lg p-6 ${className}`}>
      <h3 className="text-xl font-semibold text-white mb-4">OHLCV Candlestick Chart</h3>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="date"
            stroke="#94a3b8"
            tick={{ fill: '#94a3b8' }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis yAxisId="left" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar
            yAxisId="left"
            dataKey="high"
            fill="#10b981"
            name="High"
            opacity={0.6}
          />
          <Bar
            yAxisId="left"
            dataKey="low"
            fill="#ef4444"
            name="Low"
            opacity={0.6}
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="open"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Open"
            dot={false}
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="close"
            stroke="#eab308"
            strokeWidth={2}
            name="Close"
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CandlestickChart;

