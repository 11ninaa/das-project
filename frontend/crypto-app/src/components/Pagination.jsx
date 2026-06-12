import React from 'react';

/**
 * Reusable Pagination component showing page numbers, navigation buttons, and ellipses, with callbacks for page changes.
 */
const Pagination = ({ currentPage, totalPages, onPageChange, className = '' }) => {
  /**
   * Calculates and returns an array of page numbers to display,
   * centered on the current page with up to 5 numbers and first/last shortcuts.
   */
  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;
    let start = Math.max(0, currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages - 1, start + maxVisible - 1);

    if (end - start < maxVisible - 1) {
      start = Math.max(0, end - maxVisible + 1);
    }

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  };

  if (totalPages <= 1) return null;

  return (
    <div className={`flex items-center justify-center gap-2 ${className}`}>
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 0}
        className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-700 transition-colors"
      >
        Previous
      </button>

      {currentPage > 2 && (
        <>
          <button
            onClick={() => onPageChange(0)}
            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white hover:bg-slate-700 transition-colors"
          >
            1
          </button>
          {currentPage > 3 && <span className="text-slate-400">...</span>}
        </>
      )}

      {getPageNumbers().map((page) => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={`px-4 py-2 rounded-lg transition-colors ${
            page === currentPage
              ? 'bg-blue-600 text-white'
              : 'bg-slate-800 border border-slate-700 text-white hover:bg-slate-700'
          }`}
        >
          {page + 1}
        </button>
      ))}

      {currentPage < totalPages - 3 && (
        <>
          {currentPage < totalPages - 4 && <span className="text-slate-400">...</span>}
          <button
            onClick={() => onPageChange(totalPages - 1)}
            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white hover:bg-slate-700 transition-colors"
          >
            {totalPages}
          </button>
        </>
      )}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages - 1}
        className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-700 transition-colors"
      >
        Next
      </button>

      <span className="ml-4 text-slate-400">
        Page {currentPage + 1} of {totalPages}
      </span>
    </div>
  );
};

export default Pagination;

