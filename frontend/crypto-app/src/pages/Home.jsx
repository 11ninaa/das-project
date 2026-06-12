import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import { SkeletonCard } from '../components/LoadingSkeleton';
import { searchCrypto, getTrendingAssets } from '../services/api';
import ErrorState from '../components/ErrorState';

/**
 * Home page component displaying hero section, search bar,
 * trending crypto assets, with loading, error handling, and navigation features.
 */
const Home = () => {
  const navigate = useNavigate();
  const [trendingAssets, setTrendingAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Load trending assets when component mounts
   * Fetches the most active crypto assets to display on the home page
   */
  useEffect(() => {
    loadTrendingAssets();
  }, []);

  /**
   * Asynchronously fetches trending crypto assets,
   * updating state with fallback to default assets and handling loading and error states.
   */
  const loadTrendingAssets = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await getTrendingAssets(10);
      
      if (data && data.length > 0) {
        setTrendingAssets(data);
      } else {
        setTrendingAssets([
          { symbol: 'BTC/USD', base_asset: 'BTC', quote_asset: 'USD' },
          { symbol: 'ETH/USD', base_asset: 'ETH', quote_asset: 'USD' },
          { symbol: 'BNB/USD', base_asset: 'BNB', quote_asset: 'USD' },
          { symbol: 'ADA/USD', base_asset: 'ADA', quote_asset: 'USD' },
          { symbol: 'SOL/USD', base_asset: 'SOL', quote_asset: 'USD' },
        ]);
      }
    } catch (err) {
      console.error('Error loading trending assets:', err);
      setError('Failed to load trending assets');
      setTrendingAssets([
        { symbol: 'BTC/USD', base_asset: 'BTC', quote_asset: 'USD' },
        { symbol: 'ETH/USD', base_asset: 'ETH', quote_asset: 'USD' },
        { symbol: 'BNB/USD', base_asset: 'BNB', quote_asset: 'USD' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handles search submission by navigating to the search page with the URL-encoded crypto symbol.
   */
  const handleSearch = (symbol) => {
    if (symbol) {
      navigate(`/search?symbol=${encodeURIComponent(symbol)}`);
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center space-y-6 py-12">
        <h1 className="text-5xl font-bold text-white">Cryptocurrency Exchange Data Analyzer</h1>
        <p className="text-xl text-slate-400">
          Analyze 10 years of historical crypto exchange data with comprehensive insights
        </p>
        
        {/* Main Search Bar */}
        <div className="max-w-2xl mx-auto mt-8">
          <SearchBar
            onSelect={handleSearch}
            placeholder="Search for a crypto symbol (e.g., BTC/USD, ETH/USD)..."
            className="w-full"
          />
        </div>
      </div>

      {/* Action Button */}
      <div className="flex justify-center max-w-4xl mx-auto">
        <button
          onClick={() => navigate('/search')}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-8 rounded-lg transition-colors flex items-center justify-center space-x-2"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span>Search Historical Data</span>
        </button>
      </div>

      {/* Trending Assets */}
      <div className="max-w-6xl mx-auto">
        <h2 className="text-2xl font-semibold text-white mb-6">Most Active Assets</h2>
        
        {error && !loading && (
          <ErrorState message={error} onRetry={loadTrendingAssets} className="mb-6" />
        )}
        
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {trendingAssets.map((asset, index) => (
              <div
                key={index}
                onClick={() => handleSearch(asset.symbol)}
                className="bg-slate-800 rounded-lg p-6 hover:bg-slate-700 transition-colors cursor-pointer border border-slate-700"
              >
                <h3 className="text-xl font-bold text-white mb-3">{asset.symbol || `${asset.base_asset}/${asset.quote_asset}`}</h3>
                {asset.base_asset && asset.quote_asset && (
                  <div className="text-sm text-slate-400 space-y-1">
                    <p>Base: <span className="text-white">{asset.base_asset}</span></p>
                    <p>Quote: <span className="text-white">{asset.quote_asset}</span></p>
                  </div>
                )}
                {asset.source && (
                  <p className="text-sm text-slate-500 mt-3">Exchange: <span className="text-slate-400">{asset.source}</span></p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;

