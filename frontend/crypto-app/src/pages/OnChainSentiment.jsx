import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { getOnChainSentiment } from '../services/api';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ErrorState from '../components/ErrorState';
import SearchBar from '../components/SearchBar';
import OnChainDashboard from '../components/OnChainDashboard';
import SentimentScore from '../components/SentimentScore';
import CombinedAnalysis from '../components/CombinedAnalysis';
import ExportButtons from '../components/ExportButtons';

export default function OnChainSentiment() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [symbol, setSymbol] = useState(searchParams.get('symbol') || '');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAnalysis = async () => {
    if (!symbol || !symbol.trim()) {
      return;
    }
    
    setLoading(true);
    setError(null);
    setData(null);
    
    try {
      console.log('Fetching on-chain sentiment analysis for:', symbol);
      const result = await getOnChainSentiment(symbol);
      console.log('On-chain sentiment result:', result);
      setData(result);
    } catch (err) {
      console.error('On-chain sentiment error:', err);
      
      let errorMessage = 'Failed to fetch on-chain sentiment analysis';
      
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (symbol && symbol.trim()) {
      fetchAnalysis();
    }
  }, [symbol]);

  const handleSymbolChange = (newSymbol) => {
    console.log('Symbol changed to:', newSymbol);
    setSymbol(newSymbol);
    setSearchParams({ symbol: newSymbol });
  };

  if (loading) {
    return (
      <div>
        <LoadingSkeleton />
        <div className="mt-4 text-center text-gray-400">
          <p className="text-lg">Loading on-chain metrics and sentiment analysis...</p>
          <p className="text-sm mt-2">This may take a few seconds while fetching data from multiple APIs</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <ErrorState message={error} onRetry={fetchAnalysis} />
        <div className="mt-4 p-4 bg-yellow-900/30 border border-yellow-700/50 rounded-lg text-left max-w-2xl mx-auto">
          <p className="text-sm font-semibold text-yellow-300 mb-2">Why this error?</p>
          <p className="text-sm text-yellow-200 mb-2">
            On-chain and sentiment analysis requires:
          </p>
          <ul className="text-sm text-yellow-200 list-disc list-inside space-y-1">
            <li>Valid cryptocurrency symbol (e.g., BTC, ETH)</li>
            <li>Access to blockchain data APIs (CoinMetrics, CoinGecko, DefiLlama)</li>
            <li>Some metrics may be limited for certain cryptocurrencies</li>
          </ul>
          <p className="text-sm text-yellow-200 mt-2">
            <strong>Tip:</strong> Try popular cryptocurrencies like BTC, ETH, SOL, or BNB.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 text-white">On-Chain & Sentiment Analysis</h1>
        <p className="text-slate-300">
          Comprehensive analysis combining blockchain metrics with market sentiment
        </p>
      </div>

      {/* Search Section */}
      <div className="mb-6 space-y-4">
        <SearchBar
          initialValue={symbol}
          onSelect={handleSymbolChange}
          placeholder="Enter crypto symbol (e.g., BTC, ETH)"
        />
      </div>

      {!symbol && (
        <div className="bg-slate-800 rounded-lg shadow p-6 text-center">
          <p className="text-slate-300 text-lg mb-4">
            Enter a cryptocurrency symbol above to view on-chain metrics and sentiment analysis
          </p>
          <div className="mt-6">
            <p className="text-sm font-semibold text-blue-300 mb-4">Popular Cryptocurrencies:</p>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {['BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'XRP', 'DOGE', 'DOT', 'LTC', 'AVAX'].map((sym) => (
                <button
                  key={sym}
                  onClick={() => handleSymbolChange(sym)}
                  className="px-4 py-3 bg-slate-600 hover:bg-blue-600 text-white rounded-lg font-semibold transition-colors duration-200 shadow-md hover:shadow-lg"
                >
                  {sym}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {data && (
        <div className="space-y-6">
          {/* Combined Analysis - Show first */}
          <CombinedAnalysis
            decision={data.decision}
            onchainScore={data.onchain_details?.onchain_score}
            sentimentScore={data.sentiment_details?.sentiment_score_norm}
          />

          {/* On-Chain Dashboard */}
          <OnChainDashboard onchainDetails={data.onchain_details} />

          {/* Sentiment Analysis */}
          <SentimentScore sentiment={data.sentiment_details} />

          {/* Raw Data Section (Collapsible) */}
          <div className="bg-slate-800 rounded-lg shadow p-6">
            <details className="cursor-pointer">
              <summary className="text-lg font-semibold text-white mb-4 hover:text-blue-400">
                View Raw Data
              </summary>
              <div className="mt-4 space-y-4">
                <div>
                  <h3 className="text-sm font-semibold text-slate-400 mb-2">On-Chain Raw Data</h3>
                  <pre className="bg-slate-900 rounded p-4 overflow-x-auto text-xs text-slate-300">
                    {JSON.stringify(data.onchain_details?.raw || {}, null, 2)}
                  </pre>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-400 mb-2">Normalized Values</h3>
                  <pre className="bg-slate-900 rounded p-4 overflow-x-auto text-xs text-slate-300">
                    {JSON.stringify(data.onchain_details?.normalized || {}, null, 2)}
                  </pre>
                </div>
              </div>
            </details>
          </div>

          {/* Export Analysis Report */}
          <div className="bg-slate-800 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">Export Analysis Report</h3>
            </div>
            <ExportButtons
              data={[
                {
                  Symbol: data.symbol,
                  'Final Signal': data.decision?.signal || 'N/A',
                  'Final Score': `${((data.decision?.final_score || 0) * 100).toFixed(1)}%`,
                  'On-Chain Score': `${((data.onchain_details?.onchain_score || 0) * 100).toFixed(1)}%`,
                  'Sentiment Label': data.sentiment_details?.label || 'N/A',
                  'Sentiment Confidence': `${((data.sentiment_details?.confidence || 0) * 100).toFixed(1)}%`,
                  'Sentiment Score': data.sentiment_details?.sentiment_score_raw || 'N/A',
                  'Active Addresses': data.onchain_details?.raw?.AdrActCnt || 'N/A',
                  'Transactions': data.onchain_details?.raw?.TxCnt || 'N/A',
                  'Hash Rate': data.onchain_details?.raw?.HashRate || 'N/A',
                  'TVL': data.onchain_details?.raw?.tvl || 'N/A',
                  'NVT Ratio': data.onchain_details?.raw?.nvt || 'N/A',
                  'MVRV': data.onchain_details?.raw?.mvrv || 'N/A',
                  'Exchange Flow': data.onchain_details?.raw?.exchange_flow?.data?.[0]?.netflow || 'N/A',
                }
              ]}
              filename={`${data.symbol}_onchain_sentiment_${new Date().toISOString().split('T')[0]}`}
            />
          </div>
        </div>
      )}
    </div>
  );
}

