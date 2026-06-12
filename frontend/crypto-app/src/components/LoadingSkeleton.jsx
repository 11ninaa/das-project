import React from 'react';

/**
 * Reusable loading skeleton components providing animated placeholders for content,
 * including SkeletonCard for card-style layouts.
 */
export const SkeletonCard = () => (
  <div className="bg-slate-800 rounded-lg p-4 animate-pulse">
    <div className="h-6 bg-slate-700 rounded w-1/3 mb-3"></div>
    <div className="h-4 bg-slate-700 rounded w-1/2 mb-2"></div>
    <div className="h-4 bg-slate-700 rounded w-2/3"></div>
  </div>
);

/**
 * SkeletonTable component that shows animated placeholders for table data with configurable rows and columns.
 */
export const SkeletonTable = ({ rows = 5, cols = 6 }) => (
  <div className="animate-pulse">
    <div className="bg-slate-800 rounded-lg overflow-hidden">
      <div className="grid gap-4 p-4" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="h-4 bg-slate-700 rounded"></div>
        ))}
      </div>
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={rowIndex}
          className="grid gap-4 p-4 border-t border-slate-700"
          style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}
        >
          {Array.from({ length: cols }).map((_, colIndex) => (
            <div
              key={colIndex}
              className="h-4 bg-slate-700 rounded"
              style={{ width: colIndex === 0 ? '60%' : '100%' }}
            ></div>
          ))}
        </div>
      ))}
    </div>
  </div>
);

/**
 * SkeletonChart component providing an animated placeholder for chart components with title and chart area.
 */
export const SkeletonChart = () => (
  <div className="bg-slate-800 rounded-lg p-6 animate-pulse">
    <div className="h-6 bg-slate-700 rounded w-1/4 mb-4"></div>
    <div className="h-64 bg-slate-700 rounded"></div>
  </div>
);

export default SkeletonCard;

