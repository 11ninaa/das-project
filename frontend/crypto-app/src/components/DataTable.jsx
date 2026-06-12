import React from 'react';

/**
 * Reusable DataTable component for displaying structured data with customizable
 * columns, optional row click handling, and empty state support.
 */
const DataTable = ({ data, columns, onRowClick, className = '' }) => {
  if (!data || data.length === 0) {
    return (
      <div className={`bg-slate-800 rounded-lg p-8 text-center ${className}`}>
        <p className="text-slate-400">No data available</p>
      </div>
    );
  }

  return (
    <div className={`bg-slate-800 rounded-lg overflow-hidden ${className}`}>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-900 border-b border-slate-700">
            <tr>
              {columns.map((col, index) => (
                <th
                  key={index}
                  className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider"
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {data.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                onClick={() => onRowClick && onRowClick(row)}
                className={`hover:bg-slate-700 transition-colors ${
                  onRowClick ? 'cursor-pointer' : ''
                }`}
              >
                {columns.map((col, colIndex) => (
                  <td key={colIndex} className="px-6 py-4 whitespace-nowrap text-sm text-white">
                    {col.render ? col.render(row[col.accessor], row) : row[col.accessor]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataTable;

