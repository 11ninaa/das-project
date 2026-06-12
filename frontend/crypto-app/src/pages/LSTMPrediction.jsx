import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getLSTMPrediction } from '../services/api';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ErrorState from '../components/ErrorState';
import SearchBar from '../components/SearchBar';
import ExportButtons from '../components/ExportButtons';

export default function LSTMPrediction() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [symbol, setSymbol] = useState(searchParams.get('symbol') || '');
  const [daysAhead, setDaysAhead] = useState(7);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchPrediction = async () => {
    if (!symbol || !symbol.trim()) {
      return;
    }
    
    setLoading(true);
    setError(null);
    setData(null);
    
    try {
      console.log('Fetching LSTM prediction for:', symbol);
      const result = await getLSTMPrediction(symbol, daysAhead);
      console.log('LSTM prediction result:', result);
      setData(result);
    } catch (err) {
      console.error('LSTM prediction error:', err);
      
      let errorMessage = 'Failed to fetch LSTM prediction';
      
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message) {
        errorMessage = err.message;
        if (errorMessage.startsWith('LSTM script error: ')) {
          errorMessage = errorMessage.replace('LSTM script error: ', '');
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {

    if (symbol && symbol.trim()) {
      fetchPrediction();
    }
  }, [symbol, daysAhead]);

  const handleSymbolChange = (newSymbol) => {
    console.log('Symbol changed to:', newSymbol);
    setSymbol(newSymbol);
    setSearchParams({ symbol: newSymbol });
  };

  if (loading) {
    const preTrainedSymbols = ['BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'XRP', 'DOGE', 'DOT', 'LTC', 'AVAX'];
    const isPreTrained = symbol && preTrainedSymbols.includes(symbol.toUpperCase());
    
    return (
      <div>
        <LoadingSkeleton />
        <div className="mt-4 text-center text-gray-400">
          <p className="text-lg">
            {isPreTrained 
              ? 'Loading pre-trained model predictions...'
              : 'Training LSTM model and generating predictions...'}
          </p>
          {!isPreTrained && (
            <p className="text-sm mt-2">This may take 30-60 seconds for first-time training</p>
          )}
        </div>
      </div>
    );
  }

  if (error) {
    let errorMessage = error;
    let helpfulInfo = null;
    
    if (error.includes('Insufficient data') || error.includes('Need at least')) {
      errorMessage = `Insufficient data for ${symbol || 'this symbol'}`;
      helpfulInfo = (
        <div className="mt-4 p-4 bg-yellow-900/30 border border-yellow-700/50 rounded-lg text-left">
          <p className="text-sm font-semibold text-yellow-300 mb-2">Why this error?</p>
          <p className="text-sm text-yellow-200 mb-2">
            LSTM models require at least 20 days of historical data to make accurate predictions.
          </p>
          <p className="text-sm text-yellow-200">
            <strong>Tip:</strong> Try searching for more popular cryptocurrencies like BTC, ETH, or other pre-trained symbols.
          </p>
        </div>
      );
    }
    
    return (
      <div>
        <ErrorState message={errorMessage} onRetry={fetchPrediction} />
        {helpfulInfo}
      </div>
    );
  }

  return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6 text-white">LSTM Price Prediction</h1>
        
        {/* Search and Settings */}
        <div className="mb-6 space-y-4">
          <SearchBar
            initialValue={symbol}
            onSelect={handleSymbolChange}
            placeholder="Enter crypto symbol (e.g., BTC)"
          />
          
          <div className="flex items-center gap-4">
            <label className="font-medium text-white">Days to Predict:</label>
            <select
              value={daysAhead}
              onChange={(e) => setDaysAhead(Number(e.target.value))}
              className="border border-slate-700 rounded px-3 py-2 bg-slate-800 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>7 days</option>
              <option value={14}>14 days</option>
              <option value={30}>30 days</option>
            </select>
          </div>
        </div>

        {!symbol && (
          <div className="bg-slate-800 rounded-lg shadow p-6 text-center">
            <p className="text-slate-300 text-lg mb-4">
              Enter a cryptocurrency symbol above or click a pre-trained model below
            </p>
            <div className="mt-6">
              <p className="text-sm font-semibold text-blue-300 mb-4">Pre-trained Models (Fast Predictions):</p>
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
              <p className="text-xs text-slate-400 mt-4">
                Other symbols will be trained on-demand (may take 30-60 seconds)
              </p>
            </div>
          </div>
        )}

        {data && (
          <div className="space-y-6">
            {/* Model Info */}
            <div className="bg-slate-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4 text-white">Model Information</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-slate-400">Symbol</p>
                  <p className="text-lg font-bold text-white">{data.symbol}/{data.quote_asset}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Training Status</p>
                  <div className="flex items-center gap-2">
                    <p className="text-lg font-bold text-white">{data.training_info}</p>
                    {data.is_pre_trained && (
                      <span className="px-2 py-1 text-xs font-semibold rounded bg-blue-600 text-blue-100">
                        Pre-trained
                      </span>
                    )}
                    {data.training_type === 'on-demand' && (
                      <span className="px-2 py-1 text-xs font-semibold rounded bg-orange-600 text-orange-100">
                        On-demand
                      </span>
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Lookback Window</p>
                  <p className="text-lg font-bold text-white">{data.lookback_window} days</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Data Points</p>
                  <p className="text-lg font-bold text-white">{data.data_points}</p>
                </div>
              </div>
            </div>

            {/* Metrics */}
            <div className="bg-slate-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4 text-white">Model Performance Metrics</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-blue-900/30 border border-blue-700/50 rounded">
                  <p className="text-sm text-slate-400">RMSE</p>
                  <p className="text-2xl font-bold text-blue-400">
                    ${data.metrics.RMSE.toFixed(2)}
                  </p>
                </div>
                <div className="text-center p-4 bg-green-900/30 border border-green-700/50 rounded">
                  <p className="text-sm text-slate-400">MAPE</p>
                  <p className="text-2xl font-bold text-green-400">
                    {data.metrics.MAPE.toFixed(2)}%
                  </p>
                </div>
                <div className="text-center p-4 bg-purple-900/30 border border-purple-700/50 rounded">
                  <p className="text-sm text-slate-400">R² Score</p>
                  <p className="text-2xl font-bold text-purple-400">
                    {data.metrics.R2.toFixed(4)}
                  </p>
                </div>
              </div>
            </div>

            {/* Current Price */}
            <div className="bg-slate-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4 text-white">Current Price</h2>
              <p className="text-3xl font-bold text-white">${data.last_price.toLocaleString()}</p>
            </div>

            {/* Future Predictions */}
            <div className="bg-slate-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4 text-white">Future Price Predictions</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-700">
                  <thead className="bg-slate-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">
                        Day
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">
                        Predicted Price
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">
                        Change %
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-slate-800 divide-y divide-slate-700">
                    {data.predicted_prices.map((pred, index) => {
                      const change = ((pred.price - data.last_price) / data.last_price) * 100;
                      return (
                        <tr key={index} className="hover:bg-slate-700/50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                            Day {pred.day}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                            ${pred.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                            change >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {change >= 0 ? '+' : ''}{change.toFixed(2)}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Export Prediction Report */}
            <div className="bg-slate-800 rounded-lg p-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-white">Export Prediction Report</h3>
              </div>
              <ExportButtons
                data={[
                  {
                    Symbol: `${data.symbol}/${data.quote_asset}`,
                    'Current Price': `$${data.last_price.toLocaleString()}`,
                    'Training Status': data.training_info,
                    'Is Pre-trained': data.is_pre_trained ? 'Yes' : 'No',
                    'Training Type': data.training_type,
                    'Lookback Window': `${data.lookback_window} days`,
                    'Data Points': data.data_points,
                    'RMSE': `$${data.metrics.RMSE.toFixed(2)}`,
                    'MAPE': `${data.metrics.MAPE.toFixed(2)}%`,
                    'R² Score': data.metrics.R2.toFixed(4),
                    ...data.predicted_prices.reduce((acc, pred, index) => {
                      const change = ((pred.price - data.last_price) / data.last_price) * 100;
                      acc[`Day ${pred.day} Price`] = `$${pred.price.toFixed(2)}`;
                      acc[`Day ${pred.day} Change %`] = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
                      return acc;
                    }, {}),
                  }
                ]}
                filename={`${data.symbol}_lstm_prediction_${new Date().toISOString().split('T')[0]}`}
              />
            </div>
          </div>
        )}
      </div>
  );
}