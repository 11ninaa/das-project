import React, { useState, useEffect } from 'react';

/**
 * Reusable SearchBar component for cryptocurrency symbols with submission handling, placeholder, and optional initial value.
 */
const SearchBar = ({ onSelect, placeholder = 'Search crypto symbol...', className = '', initialValue = '' }) => {
  const [query, setQuery] = useState(initialValue);

  /**
   * Update query state when initialValue prop changes
   * This allows the search bar to be controlled externally (e.g., from URL parameters)
   */
  useEffect(() => {
    if (initialValue) {
      setQuery(initialValue);
    }
  }, [initialValue]);

  /**
   * Handles form submission by preventing default behavior and calling onSelect with a non-empty trimmed query.
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    if (query && query.trim() && onSelect) {
      onSelect(query.trim());
    }
  };

  return (
    <div className={className}>
      <form onSubmit={handleSubmit} className="relative flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="flex-1 px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-slate-400"
        />
        <button
          type="submit"
          disabled={!query || !query.trim()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-600 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
        >
          Search
        </button>
      </form>
    </div>
  );
};

export default SearchBar;

