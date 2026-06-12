import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getTechnicalAnalysis } from '../services/api';
import SignalBadge from '../components/SignalBadge';
import TechnicalIndicators from '../components/TechnicalIndicators';
import TimeframeSelector from '../components/TimeframeSelector';
import ErrorState from '../components/ErrorState';
import LoadingSkeleton from '../components/LoadingSkeleton';
import SearchBar from '../components/SearchBar';
import ExportButtons from '../components/ExportButtons';

function TechnicalAnalysis() {
  const { symbol } = useParams();
  const navigate = useNavigate();
  const [timeframe, setTimeframe] = useState('1d');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (symbol) {
      loadAnalysis();
    } else {
      navigate('/analysis');
    }
  }, [symbol, timeframe, navigate]);

  const loadAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getTechnicalAnalysis(symbol, timeframe);
      setAnalysis(data);
    } catch (err) {
      console.error('Error loading analysis:', err);
      setError(err.response?.data?.error || err.message || 'Failed to load technical analysis');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <LoadingSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <ErrorState
          message={error}
          onRetry={loadAnalysis}
        />
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-slate-800 rounded-lg p-6 text-center">
          <p className="text-slate-300 text-lg">No analysis data available for {symbol}</p>
          <button
            onClick={() => navigate('/analysis')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Select Another Symbol
          </button>
        </div>
      </div>
    );
  }

  const handleSymbolSearch = (searchQuery) => {
    if (searchQuery && searchQuery.trim()) {
      const cleanSymbol = searchQuery.trim().split('/')[0].toUpperCase();
      navigate(`/analysis/${cleanSymbol}`);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-4 text-white">Technical Analysis: {symbol}</h1>

        <div className="max-w-md">
          <SearchBar
            onSelect={handleSymbolSearch}
            placeholder="Search for another symbol (e.g., BTC, ETH)..."
            initialValue=""
          />
        </div>
      </div>

      <TimeframeSelector
        timeframe={timeframe}
        onChange={setTimeframe}
      />

      <SignalBadge
        signal={analysis.signal}
        confidence={analysis.confidence}
        reasoning={analysis.reasoning}
      />

      <TechnicalIndicators
        indicators={analysis.indicators || {}}
        votes={{
          buy: analysis.buy_votes || 0,
          sell: analysis.sell_votes || 0,
          neutral: analysis.neutral_votes || 0
        }}
      />

      {/* Export Analysis Report */}
      {analysis && (
        <div className="bg-slate-800 rounded-lg p-4 mt-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-white">Export Analysis Report</h3>
          </div>
          <ExportButtons
            data={[
              {
                Symbol: symbol,
                Timeframe: timeframe,
                Signal: analysis.signal,
                Confidence: `${((analysis.confidence || 0) * 100).toFixed(1)}%`,
                'Buy Votes': analysis.buy_votes || 0,
                'Sell Votes': analysis.sell_votes || 0,
                'Neutral Votes': analysis.neutral_votes || 0,
                Reasoning: analysis.reasoning || '',
                ...Object.entries(analysis.indicators || {}).reduce((acc, [key, value]) => {
                  if (typeof value === 'object' && value !== null) {
                    acc[`${key}_value`] = value.value || value.signal || 'N/A';
                    acc[`${key}_signal`] = value.signal || 'N/A';
                  } else {
                    acc[key] = value || 'N/A';
                  }
                  return acc;
                }, {}),
              }
            ]}
            filename={`${symbol}_technical_analysis_${timeframe}`}
          />
        </div>
      )}
    </div>
  );
}

export default TechnicalAnalysis;