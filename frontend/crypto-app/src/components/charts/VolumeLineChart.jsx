import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

/**
 * VolumeLineChart Component
 * 
 * Displays trading volume and number of trades over time as a line chart.
 * Uses two Y-axes: left axis for volume (in quote currency) and right axis for number of trades.
 * Includes interactive tooltips showing detailed volume and trade information.
 * 
 * @param {Array<Object>} data - Array of stock price objects with volume and trade data
 * @param {string} className - Additional CSS classes to apply to the chart container
 * @param {string} id - ID for the component (for export functionality)
 * @returns {JSX.Element} Volume line chart component or empty state message
 */
const VolumeLineChart = ({ data, className = '', id = 'volume-line-chart' }) => {
  if (!data || data.length === 0) {
    return (
      <div id={id} className={`bg-slate-800 rounded-lg p-8 text-center ${className}`}>
        <p className="text-slate-400">No volume data available</p>
      </div>
    );
  }

  /**
   * Format data for volume line chart visualization
   * Extracts volume (quote_volume) and number of trades from each data item
   * 
   * @returns {Array<Object>} Array of chart data points with date, volume, and trades
   */
  const chartData = data.map((item) => ({
    date: item.date || '',
    volume: parseFloat(item.quote_volume) || 0,
    trades: parseInt(item.number_of_trades) || 0,
  }));

  /**
   * Custom tooltip component for the volume chart
   * Displays detailed volume and trade information when hovering over chart lines
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
          <p className="text-blue-400">Volume: ${data.volume?.toLocaleString(2)}</p>
          <p className="text-purple-400">Trades: {data.trades?.toLocaleString()}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div id={id} className={`bg-slate-800 rounded-lg p-6 ${className}`}>
      <h3 className="text-xl font-semibold text-white mb-4">Volume & Trading Activity</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
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
          <YAxis yAxisId="right" orientation="right" stroke="#a855f7" tick={{ fill: '#a855f7' }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="volume"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Volume (Quote)"
            dot={false}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="trades"
            stroke="#a855f7"
            strokeWidth={2}
            name="Number of Trades"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default VolumeLineChart;

