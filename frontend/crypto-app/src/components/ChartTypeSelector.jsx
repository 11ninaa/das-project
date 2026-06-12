import React from 'react';

/**
 * Component for selecting chart types via buttons, configurable with custom types and handling changes through a callback.
 */
const ChartTypeSelector = ({ selectedType = 'candlestick', onChange, className = '', types = null }) => {
  const defaultChartTypes = [
    { value: 'candlestick', label: 'Candlestick' },
    { value: 'line', label: 'Line' },
    { value: 'bar', label: 'Bar' },
  ];
  
  const chartTypes = types || defaultChartTypes;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-slate-300 text-sm font-medium mr-2">Chart Type:</span>
      <div className="flex gap-2">
        {chartTypes.map((type) => (
          <button
            key={type.value}
            onClick={() => onChange(type.value)}
            className={`px-4 py-2 rounded-md transition-colors ${
              selectedType === type.value
                ? 'bg-blue-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
            title={`Switch to ${type.label} chart`}
          >
            <span className="text-sm font-medium">{type.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ChartTypeSelector;

