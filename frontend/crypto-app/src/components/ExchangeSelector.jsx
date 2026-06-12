import React from 'react';

/**
 * Dropdown component for selecting or filtering by exchange, with an "All Exchanges" option and change callback support.
 */
const ExchangeSelector = ({ exchanges, selectedExchange, onSelect, className = '' }) => {
  return (
    <div className={className}>
      <label className="block text-sm font-medium text-slate-300 mb-2">Filter by Exchange</label>
      <select
        value={selectedExchange || ''}
        onChange={(e) => onSelect(e.target.value || null)}
        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white"
      >
        <option value="">All Exchanges</option>
        {exchanges.map((exchange) => (
          <option key={exchange} value={exchange}>
            {exchange}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ExchangeSelector;

