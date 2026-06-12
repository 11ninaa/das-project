import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchBar from '../components/SearchBar';

/**
 * Page component for selecting a cryptocurrency symbol to view technical analysis,
 * featuring search and navigation to the analysis page.
 */
const AnalysisSelector = () => {
  const navigate = useNavigate();
  const [symbol, setSymbol] = useState('');

  const handleSearch = (searchQuery) => {
    if (searchQuery && searchQuery.trim()) {
      const cleanSymbol = searchQuery.trim().split('/')[0].toUpperCase();
      navigate(`/analysis/${cleanSymbol}`);
    }
  };

  const handleQuickSelect = (quickSymbol) => {
    navigate(`/analysis/${quickSymbol}`);
  };

  const popularSymbols = ['BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'XRP', 'DOT', 'DOGE', 'AVAX', 'LTC'];

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-4xl font-bold mb-2 text-white">Technical Analysis</h1>
      <p className="text-slate-300 mb-8">
        Select a cryptocurrency to view detailed technical analysis with indicators and trading signals
      </p>

      <div className="bg-slate-800 rounded-lg p-6 mb-8">
        <label className="block text-white font-semibold mb-2">
          Search for a Cryptocurrency
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch(symbol)}
            placeholder="Enter symbol (e.g., BTC, ETH)"
            className="flex-1 px-4 py-2 rounded-md bg-slate-700 text-white border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => handleSearch(symbol)}
            disabled={!symbol.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors"
          >
            Analyze
          </button>
        </div>
      </div>

      {/* Quick Select Section */}
      <div className="bg-slate-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Popular Cryptocurrencies</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {popularSymbols.map((sym) => (
            <button
              key={sym}
              onClick={() => handleQuickSelect(sym)}
              className="px-4 py-3 bg-slate-700 text-white rounded-md hover:bg-blue-600 transition-colors font-medium"
            >
              {sym}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnalysisSelector;

