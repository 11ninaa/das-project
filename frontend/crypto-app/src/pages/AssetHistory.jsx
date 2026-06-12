import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import ExchangeSelector from '../components/ExchangeSelector';
import DataTable from '../components/DataTable';
import ErrorState from '../components/ErrorState';
import { SkeletonChart, SkeletonTable } from '../components/LoadingSkeleton';
import CandlestickChart from '../components/charts/CandlestickChart';
import LineChart from '../components/charts/LineChart';
import BarChart from '../components/charts/BarChart';
import VolumeLineChart from '../components/charts/VolumeLineChart';
import VolumeBarChart from '../components/charts/VolumeBarChart';
import ChartTypeSelector from '../components/ChartTypeSelector';
import ExportButtons from '../components/ExportButtons';
import { getExchanges, searchCrypto, getCryptoHistory } from '../services/api';

/**
 * Page component for viewing a cryptocurrency's historical data, featuring charts,
 * tables, filtering by date and exchange, and fallback data handling.
 */
const AssetHistory = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [symbol, setSymbol] = useState(() => {
    const symbolParam = searchParams.get('symbol');
    return symbolParam ? decodeURIComponent(symbolParam) : '';
  });
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [singleDate, setSingleDate] = useState('');
  const [dateMode, setDateMode] = useState('range'); // 'single' or 'range'
  const [selectedExchange, setSelectedExchange] = useState(null);
  const [exchanges, setExchanges] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [exchangesLoading, setExchangesLoading] = useState(false);
  const [chartType, setChartType] = useState('candlestick');
  const [volumeChartType, setVolumeChartType] = useState('bar');

  const symbolFromUrl = searchParams.get('symbol');
  
  /**
   * Load symbol from URL params and load exchange list on component mount
   * Updates symbol state when URL parameter changes (e.g., navigation from search page)
   */
  useEffect(() => {
    if (symbolFromUrl) {
      setSymbol(decodeURIComponent(symbolFromUrl));
    } else {
      setSymbol('');
    }
    loadExchanges();
  }, [symbolFromUrl]);

  /**
   * Fetch historical data when symbol, date(s), or exchange filter changes
   * Automatically triggers data fetch when user selects dates or changes filters
   */
  useEffect(() => {
    if (symbol && (singleDate || (fromDate && toDate))) {
      fetchHistoricalData();
    }
  }, [symbol, fromDate, toDate, singleDate, selectedExchange]);

  /**
   * Asynchronously fetches available exchanges to populate the filter dropdown, continuing silently if the request fails.
   */
  const loadExchanges = async () => {
    try {
      setExchangesLoading(true);
      const data = await getExchanges();
      setExchanges(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error loading exchanges:', err);
      // Continue without exchange filter if it fails
    } finally {
      setExchangesLoading(false);
    }
  };

  /**
   * Asynchronously fetches historical data for a symbol and date range,
   * with optional exchange filtering, automatic fallback to client-side filtering, and error handling.
   */
  const fetchHistoricalData = async () => {
    if (!symbol) return;

    try {
      setLoading(true);
      setError(null);

      let from = fromDate;
      let to = toDate;

      if (dateMode === 'single' && singleDate) {
        from = singleDate;
        to = singleDate;
      }

      if (!from || !to) {
        setHistoricalData([]);
        setLoading(false);
        return;
      }

      let data = [];
      try {
        const historyData = await getCryptoHistory(symbol, from, to, selectedExchange);
        data = Array.isArray(historyData) ? historyData : [];
      } catch (historyError) {
        if (historyError.response?.status === 404) {
          let allData = [];
          let currentPage = 0;
          let hasMore = true;
          const maxRecords = 5000;
          
          while (hasMore && allData.length < maxRecords) {
            const searchResults = await searchCrypto(symbol, currentPage, 100);
            const pageData = searchResults.content || [];
            
            if (pageData.length === 0) {
              hasMore = false;
            } else {
              allData = [...allData, ...pageData];
              currentPage++;
              
              if (pageData.length < 100) {
                hasMore = false;
              }
            }
          }
          
          const fromDateObj = new Date(from + 'T00:00:00');
          const toDateObj = new Date(to + 'T23:59:59');
          
          data = allData.filter(item => {
            if (!item.date) return false;
            const itemDate = new Date(item.date);
            return itemDate >= fromDateObj && itemDate <= toDateObj;
          });

          if (selectedExchange) {
            data = data.filter(item => item.source === selectedExchange);
          }

          if (data.length === 0 && allData.length > 0) {
            setError(`No data found for the selected date range (${from} to ${to}). Found ${allData.length} total records for ${symbol}, but none match the date filter.`);
          } else if (data.length === 0) {
            setError(`No data found for symbol "${symbol}". Please check the symbol name and try again.`);
          }
        } else {
          throw historyError;
        }
      }

      data.sort((a, b) => new Date(a.date) - new Date(b.date));
      
      setHistoricalData(data);
    } catch (err) {
      console.error('Error fetching historical data:', err);
      setError('Failed to fetch historical data. Please check your inputs and try again.');
      setHistoricalData([]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Updates the selected crypto symbol state and URL parameter for bookmarking and direct linking when a symbol is chosen.
   */
  const handleSymbolSelect = (selectedSymbol) => {
    setSymbol(selectedSymbol);
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set('symbol', selectedSymbol);
    navigate(`/history?${newSearchParams.toString()}`, { replace: true });
  };

  /**
   * Formats OHLCV data into a readable string showing Open, High, Low, and Close values.
   */
  const formatOHLCV = (ohlcv) => {
    if (!ohlcv) return 'N/A';
    if (typeof ohlcv === 'object') {
      const o = ohlcv.open || 'N/A';
      const h = ohlcv.high || 'N/A';
      const l = ohlcv.low || 'N/A';
      const c = ohlcv.close || 'N/A';
      return `O: ${o} | H: ${h} | L: ${l} | C: ${c}`;
    }
    return ohlcv;
  };

  /**
   * Formats a number with thousand separators and decimals, returning "N/A" if invalid.
   */
  const formatNumber = (num) => {
    if (!num) return 'N/A';
    return parseFloat(num).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  /**
   * Groups historical data by exchange, returning an object with exchange names as keys and corresponding data arrays as values.
   */
  const dataByExchange = historicalData.reduce((acc, item) => {
    const source = item.source || 'Unknown';
    if (!acc[source]) {
      acc[source] = [];
    }
    acc[source].push(item);
    return acc;
  }, {});

  const columns = [
    {
      header: 'Date',
      accessor: 'date',
    },
    {
      header: 'Exchange',
      accessor: 'source',
      render: (value) => <span className="text-purple-400 font-semibold">{value || 'N/A'}</span>,
    },
    {
      header: 'OHLCV',
      accessor: 'ohlcv',
      render: (value) => <span className="text-sm">{formatOHLCV(value)}</span>,
    },
    {
      header: 'Quote Volume',
      accessor: 'quote_volume',
      render: (value) => <span className="text-green-400">${formatNumber(value)}</span>,
    },
    {
      header: 'Number of Trades',
      accessor: 'number_of_trades',
      render: (value) => <span className="text-blue-400">{formatNumber(value)}</span>,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-4">Asset Historical Data</h1>
        <p className="text-slate-400 mb-6">
          View detailed historical OHLCV data, volume, and trading metrics for any cryptocurrency
        </p>
      </div>

      {/* Controls */}
      <div className="bg-slate-800 rounded-lg p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Crypto Symbol</label>
          <SearchBar 
            onSelect={handleSymbolSelect} 
            placeholder="Select or enter symbol..." 
            initialValue={symbol}
          />
        </div>

        {/* Date Mode Selection */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Date Selection Mode</label>
          <div className="flex gap-4">
            <button
              onClick={() => {
                setDateMode('range');
                setSingleDate('');
              }}
              className={`px-4 py-2 rounded-lg transition-colors ${
                dateMode === 'range'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Date Range
            </button>
            <button
              onClick={() => {
                setDateMode('single');
                setFromDate('');
                setToDate('');
              }}
              className={`px-4 py-2 rounded-lg transition-colors ${
                dateMode === 'single'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Single Date
            </button>
          </div>
        </div>

        {/* Date Inputs */}
        {dateMode === 'range' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">From Date</label>
              <input
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">To Date</label>
              <input
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
              />
            </div>
          </div>
        ) : (
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Date</label>
            <input
              type="date"
              value={singleDate}
              onChange={(e) => setSingleDate(e.target.value)}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
            />
          </div>
        )}

        {/* Exchange Filter */}
        {exchanges.length > 0 && (
          <ExchangeSelector
            exchanges={exchanges}
            selectedExchange={selectedExchange}
            onSelect={setSelectedExchange}
          />
        )}

        {symbol && (
          <div className="pt-4 border-t border-slate-700">
            <p className="text-slate-300">
              <span className="font-semibold">Selected Symbol:</span>{' '}
              <span className="text-blue-400">{symbol}</span>
            </p>
          </div>
        )}
      </div>

      {error && <ErrorState message={error} onRetry={fetchHistoricalData} />}

      {/* Export Buttons Section */}
      {historicalData.length > 0 && (
        <div className="bg-slate-800 rounded-lg p-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-white">Export Options</h3>
          </div>
          <ExportButtons
            data={historicalData.map(item => {
              const ohlcv = typeof item.ohlcv === 'object' ? item.ohlcv : {};
              return {
                Date: item.date || '',
                Symbol: symbol || '',
                Exchange: item.source || 'N/A',
                Open: ohlcv.open || item.open || 'N/A',
                High: ohlcv.high || item.high || 'N/A',
                Low: ohlcv.low || item.low || 'N/A',
                Close: ohlcv.close || item.close || 'N/A',
                Volume: item.quote_volume || item.volume || 0,
                'Number of Trades': item.number_of_trades || 0,
              };
            })}
            charts={[
              { 
                id: chartType === 'candlestick' ? 'candlestick-chart' : 
                    chartType === 'line' ? 'line-chart' : 'bar-chart', 
                title: `OHLCV ${chartType.charAt(0).toUpperCase() + chartType.slice(1)} Chart` 
              },
              { 
                id: volumeChartType === 'line' ? 'volume-line-chart' : 'volume-bar-chart', 
                title: `Volume ${volumeChartType.charAt(0).toUpperCase() + volumeChartType.slice(1)} Chart` 
              },
            ]}
            filename={`${symbol || 'crypto'}_historical_data_${fromDate || singleDate || 'all'}_${toDate || singleDate || 'all'}`}
          />
        </div>
      )}

      {/* Charts and Data */}
      {loading ? (
        <div className="space-y-6">
          <SkeletonChart />
          <SkeletonChart />
          <SkeletonTable rows={10} cols={5} />
        </div>
      ) : (
        <>
          {historicalData.length > 0 && (
            <>
              {/* OHLCV Chart - Dynamic based on selected type */}
              <div className="space-y-4">
                <div className="flex justify-end">
                  <ChartTypeSelector 
                    selectedType={chartType} 
                    onChange={setChartType}
                  />
                </div>
                {chartType === 'candlestick' && (
                  <CandlestickChart data={historicalData} id="candlestick-chart" />
                )}
                {chartType === 'line' && (
                  <LineChart data={historicalData} id="line-chart" />
                )}
                {chartType === 'bar' && (
                  <BarChart data={historicalData} id="bar-chart" />
                )}
              </div>

              {/* Volume Chart - Dynamic based on selected type */}
              <div className="space-y-4">
                <div className="flex justify-end">
                  <ChartTypeSelector 
                    selectedType={volumeChartType} 
                    onChange={setVolumeChartType}
                    types={[
                      { value: 'line', label: 'Line' },
                      { value: 'bar', label: 'Bar' },
                    ]}
                  />
                </div>
                {volumeChartType === 'line' && (
                  <VolumeLineChart data={historicalData} id="volume-line-chart" />
                )}
                {volumeChartType === 'bar' && (
                  <VolumeBarChart data={historicalData} id="volume-bar-chart" />
                )}
              </div>

              {/* Data Table */}
              <div>
                <h2 className="text-2xl font-semibold text-white mb-4">Historical Data Table</h2>
                <DataTable data={historicalData} columns={columns} />
              </div>

              {/* Breakdown by Exchange */}
              {Object.keys(dataByExchange).length > 1 && (
                <div className="space-y-4">
                  <h2 className="text-2xl font-semibold text-white">Breakdown by Exchange</h2>
                  {Object.entries(dataByExchange).map(([exchange, data]) => (
                    <div key={exchange} className="bg-slate-800 rounded-lg p-4">
                      <h3 className="text-xl font-semibold text-purple-400 mb-4">{exchange}</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-slate-400">Total Records</p>
                          <p className="text-white text-lg font-semibold">{data.length}</p>
                        </div>
                        <div>
                          <p className="text-slate-400">Total Volume</p>
                          <p className="text-green-400 text-lg font-semibold">
                            ${data.reduce((sum, item) => sum + (parseFloat(item.quote_volume) || 0), 0).toLocaleString(2)}
                          </p>
                        </div>
                        <div>
                          <p className="text-slate-400">Total Trades</p>
                          <p className="text-blue-400 text-lg font-semibold">
                            {data.reduce((sum, item) => sum + (parseInt(item.number_of_trades) || 0), 0).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {!loading && historicalData.length === 0 && symbol && (singleDate || (fromDate && toDate)) && (
            <div className="bg-slate-800 rounded-lg p-12 text-center">
              <p className="text-slate-400 text-lg">No historical data found for the selected criteria</p>
            </div>
          )}

          {!symbol && (
            <div className="bg-slate-800 rounded-lg p-12 text-center">
              <p className="text-slate-400 text-lg">Please select a cryptocurrency symbol to view historical data</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default AssetHistory;

