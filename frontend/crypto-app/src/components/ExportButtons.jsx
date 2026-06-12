import React from 'react';
import { exportToCSV, exportChartToPDF, exportMultipleChartsToPDF } from '../utils/exportUtils';

/**
 * Component providing buttons to export data and charts in various formats with customizable filename and styling.
 */
const ExportButtons = ({ data, charts = [], filename = 'export', className = '' }) => {
  const handleExportCSV = () => {
    if (!data || data.length === 0) {
      alert('No data to export');
      return;
    }
    exportToCSV(data, filename);
  };

  const handleExportChartsPDF = async () => {
    if (charts.length === 0) {
      alert('No charts to export');
      return;
    }
    await exportMultipleChartsToPDF(charts, `${filename}_charts`);
  };

  const handleExportSingleChartPDF = async (chartId, chartTitle) => {
    await exportChartToPDF(chartId, `${filename}_${chartId}`, chartTitle);
  };

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {data && data.length > 0 && (
        <button
          onClick={handleExportCSV}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md transition-colors flex items-center gap-2"
          title="Export data to CSV"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export CSV
        </button>
      )}
      
      {charts.length > 0 && (
        <button
          onClick={handleExportChartsPDF}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors flex items-center gap-2"
          title="Export all charts to PDF"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          Export Charts PDF
        </button>
      )}
    </div>
  );
};

export default ExportButtons;

