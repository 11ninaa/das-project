import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import DataTable from '../components/DataTable';
import Pagination from '../components/Pagination';
import { SkeletonTable } from '../components/LoadingSkeleton';
import ErrorState from '../components/ErrorState';
import { searchCrypto } from '../services/api';

/**
 * Page component for searching and displaying cryptocurrencies with paginated results,
 * row navigation, URL parameter support, and loading/error handling.
 */
const CryptoSearch = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('symbol') || '');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [totalElements, setTotalElements] = useState(0);
  const pageSize = 20;

  /**
   * Check for symbol parameter in URL and perform search if present
   * Allows the page to load with a search query from URL (e.g., from home page navigation)
   */
  useEffect(() => {
    const symbolParam = searchParams.get('symbol');
    if (symbolParam) {
      setQuery(symbolParam);
      performSearch(symbolParam, 0);
    }
  }, [searchParams]);

  /**
   * Performs a paginated search for cryptocurrency symbols, updates URL parameters, and handles different API response formats.
   */
  const performSearch = async (searchQuery, page = 0) => {
    if (!searchQuery || searchQuery.trim().length < 1) {
      setResults([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await searchCrypto(searchQuery, page, pageSize);
      
      if (Array.isArray(response)) {
        setResults(response);
        setTotalPages(Math.ceil(response.length / pageSize));
        setTotalElements(response.length);
      } else {
        setResults(response.content || []);
        setTotalPages(response.totalPages || 0);
        setTotalElements(response.totalElements || response.content?.length || 0);
      }
      
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set('symbol', searchQuery);
      newSearchParams.set('page', page);
      navigate(`/search?${newSearchParams.toString()}`, { replace: true });
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to search cryptocurrency data. Please try again.');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle search bar submission
   * Resets to page 0 and performs a new search with the provided symbol.
   * @param {string} symbol - The crypto symbol to search for
   */
  const handleSearch = (symbol) => {
    if (symbol) {
      setQuery(symbol);
      setCurrentPage(0);
      performSearch(symbol, 0);
    }
  };

  /**
   * Handle pagination page change
   * Updates the current page and performs search for the new page.
   * Scrolls to top of page for better UX.
   * @param {number} newPage - The new page number (0-indexed)
   */
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    performSearch(query, newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  /**
   * Handle table row click
   * Navigates to the historical data page for the clicked symbol.
   * @param {Object} row - The row data object containing the symbol
   */
  const handleRowClick = (row) => {
    navigate(`/history?symbol=${encodeURIComponent(row.symbol)}`);
  };

  /**
   * Formats OHLCV data (object or string) into a readable string showing Open, High, Low, and Close values.
   */
  const formatOHLCV = (ohlcv) => {
    if (!ohlcv) return 'N/A';
    if (typeof ohlcv === 'object') {
      return `O: ${ohlcv.open || 'N/A'} | H: ${ohlcv.high || 'N/A'} | L: ${ohlcv.low || 'N/A'} | C: ${ohlcv.close || 'N/A'}`;
    }
    return ohlcv;
  };

  /**
   * Formats a volume value as currency with thousand separators, returning "N/A" if invalid.
   */
  const formatVolume = (volume) => {
    if (!volume) return 'N/A';
    return `$${parseFloat(volume).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const columns = [
    {
      header: 'Symbol',
      accessor: 'symbol',
      render: (value) => <span className="font-semibold text-blue-400">{value}</span>,
    },
    {
      header: 'Base Asset',
      accessor: 'base_asset',
    },
    {
      header: 'Quote Asset',
      accessor: 'quote_asset',
    },
    {
      header: 'Exchange',
      accessor: 'source',
      render: (value) => <span className="text-purple-400">{value || 'N/A'}</span>,
    },
    {
      header: 'OHLCV',
      accessor: 'ohlcv',
      render: (value) => (
        <span className="text-sm text-slate-300">{formatOHLCV(value)}</span>
      ),
    },
    {
      header: 'Volume',
      accessor: 'quote_volume',
      render: (value) => <span className="text-green-400">{formatVolume(value)}</span>,
    },
    {
      header: 'Date',
      accessor: 'date',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-4">Cryptocurrency Search</h1>
        <p className="text-slate-400 mb-6">
          Search for cryptocurrency assets across multiple exchanges and view their latest data
        </p>
      </div>

      {/* Search Bar */}
      <div className="max-w-2xl">
        <SearchBar onSelect={handleSearch} placeholder="Search by symbol (e.g., BTC/USD)..." />
      </div>

      {/* Results Count */}
      {!loading && results.length > 0 && (
        <div className="text-slate-400">
          Found {totalElements} result{totalElements !== 1 ? 's' : ''}
        </div>
      )}

      {/* Error State */}
      {error && <ErrorState message={error} onRetry={() => performSearch(query, currentPage)} />}

      {/* Results Table */}
      {loading ? (
        <SkeletonTable rows={10} cols={7} />
      ) : (
        <>
          <DataTable
            data={results}
            columns={columns}
            onRowClick={handleRowClick}
          />

          {/* Pagination */}
          {totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          )}

          {/* Empty State */}
          {!loading && results.length === 0 && query && (
            <div className="bg-slate-800 rounded-lg p-12 text-center">
              <p className="text-slate-400 text-lg">No results found for "{query}"</p>
              <p className="text-slate-500 mt-2">Try searching with a different symbol</p>
            </div>
          )}

          {!loading && !query && (
            <div className="bg-slate-800 rounded-lg p-12 text-center">
              <p className="text-slate-400 text-lg">Enter a symbol to start searching</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default CryptoSearch;

