import React, { useState } from 'react';

/**
 * Help page component providing documentation, usage instructions,
 * and guidance on features, charts, exports, and troubleshooting.
 */
const Help = () => {
  const [activeSection, setActiveSection] = useState('getting-started');

  const sections = [
    { id: 'getting-started', title: 'Getting Started' },
    { id: 'features', title: 'Features Overview' },
    { id: 'search', title: 'Search & Browse' },
    { id: 'historical-data', title: 'Historical Data' },
    { id: 'charts', title: 'Charts & Visualizations' },
    { id: 'technical-analysis', title: 'Technical Analysis' },
    { id: 'onchain-sentiment', title: 'On-Chain & Sentiment' },
    { id: 'lstm-prediction', title: 'LSTM Predictions' },
    { id: 'export', title: 'Export Options' },
    { id: 'troubleshooting', title: 'Troubleshooting' },
  ];

  const renderContent = () => {
    switch (activeSection) {
      case 'getting-started':
        return (
          <div className="space-y-4">
            <h3 className="text-2xl font-semibold text-white mb-4">Getting Started</h3>
            <div className="space-y-3 text-slate-300">
              <p>
                Welcome to Crypto Analyzer! This application helps you analyze cryptocurrency data
                with advanced technical indicators, visualizations, and AI-powered predictions.
              </p>
              <div>
                <h4 className="text-xl font-semibold text-white mt-6 mb-3">Quick Start Guide</h4>
                <ol className="list-decimal list-inside space-y-2 ml-4">
                  <li>Use the <strong>Search</strong> page to find cryptocurrencies by name or symbol</li>
                  <li>Navigate to <strong>Historical Data</strong> to view price history and charts</li>
                  <li>Access <strong>Technical Analysis</strong> for detailed indicator analysis</li>
                  <li>Use <strong>On-Chain & Sentiment Analysis</strong> for blockchain metrics and market sentiment</li>
                  <li>Check <strong>LSTM Predictions</strong> for AI-powered price forecasts</li>
                </ol>
              </div>
            </div>
          </div>
        );

      case 'features':
        return (
          <div className="space-y-4">
            <h3 className="text-2xl font-semibold text-white mb-4">Features Overview</h3>
            <div className="space-y-4 text-slate-300">
              <div className="bg-slate-800 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-2">Search & Browse</h4>
                <p>Search for cryptocurrencies by name or symbol. View trending coins and filter by exchange.</p>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-2">Historical Data</h4>
                <p>View detailed OHLCV (Open, High, Low, Close, Volume) data with interactive charts and date range filtering.</p>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-2">Multiple Chart Types</h4>
                <p>Switch between Candlestick, Line, and Bar charts for both OHLCV and Volume data.</p>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-2">Technical Analysis</h4>
                <p>Get comprehensive technical indicators including RSI, MACD, Moving Averages, Bollinger Bands, and more.</p>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-2">On-Chain & Sentiment Analysis</h4>
                <p>Combines blockchain metrics (addresses, transactions, hash rate, TVL, NVT, MVRV) with sentiment analysis from Reddit, CryptoPanic, and NewsAPI.</p>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-2">LSTM Predictions</h4>
                <p>AI-powered price predictions using Long Short-Term Memory neural networks.</p>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-2">Export Options</h4>
                <p>Export data to CSV and charts to PDF for further analysis or reporting.</p>
              </div>
            </div>
          </div>
        );

      case 'search':
        return (
          <div className="space-y-4">
            <h3 className="text-2xl font-semibold text-white mb-4">Search & Browse Cryptocurrencies</h3>
            <div className="space-y-3 text-slate-300">
              <p>Use the Search page to find cryptocurrencies:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Enter a cryptocurrency name or symbol in the search bar</li>
                <li>Results will show matching cryptocurrencies with their symbols</li>
                <li>Click on a result to view detailed information</li>
                <li>Use the Exchange filter to filter results by exchange/source</li>
                <li>View trending cryptocurrencies in the trending section</li>
              </ul>
            </div>
          </div>
        );

      case 'historical-data':
        return (
          <div className="space-y-4">
            <h3 className="text-2xl font-semibold text-white mb-4">Historical Data</h3>
            <div className="space-y-3 text-slate-300">
              <p>The Historical Data page allows you to:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>Select a Cryptocurrency:</strong> Use the search bar to find and select a crypto symbol</li>
                <li><strong>Choose Date Range:</strong> Select either a single date or a date range</li>
                <li><strong>Filter by Exchange:</strong> Optionally filter data by specific exchange/source</li>
                <li><strong>View Charts:</strong> See OHLCV and Volume charts with multiple chart type options</li>
                <li><strong>View Data Table:</strong> Browse detailed historical records in a sortable table</li>
                <li><strong>Export Data:</strong> Download data as CSV or charts as PDF</li>
              </ul>
            </div>
          </div>
        );

      case 'charts':
        return (
          <div className="space-y-4">
            <h3 className="text-2xl font-semibold text-white mb-4">Charts & Visualizations</h3>
            <div className="space-y-4 text-slate-300">
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">OHLCV Chart Types</h4>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong>Candlestick:</strong> Shows high/low as bars and open/close as lines</li>
                  <li><strong>Line:</strong> Displays open, high, low, and close as separate lines</li>
                  <li><strong>Bar:</strong> Shows all OHLC values as bars</li>
                </ul>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Volume Chart Types</h4>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong>Line:</strong> Shows volume and number of trades as lines</li>
                  <li><strong>Bar:</strong> Displays volume and number of trades as bars</li>
                </ul>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Using Charts</h4>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Hover over chart elements to see detailed tooltips</li>
                  <li>Use the chart type selector above each chart to switch between types</li>
                  <li>Charts are responsive and adjust to your screen size</li>
                  <li>Export charts to PDF using the export buttons</li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 'technical-analysis':
        return (
          <div className="space-y-4">
            <h3 className="text-2xl font-semibold text-white mb-4">Technical Analysis</h3>
            <div className="space-y-3 text-slate-300">
              <p>The Technical Analysis page provides:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>Technical Indicators:</strong> RSI, MACD, Moving Averages, Bollinger Bands, and more</li>
                <li><strong>Buy/Sell/Neutral Signals:</strong> Based on indicator analysis</li>
                <li><strong>Confidence Score:</strong> Percentage indicating signal strength</li>
                <li><strong>Timeframe Selection:</strong> Choose from 1d, 7d, 30d, or 90d</li>
                <li><strong>Detailed Reasoning:</strong> Explanation of the analysis results</li>
              </ul>
              <div className="bg-slate-800 rounded-lg p-4 mt-4">
                <h4 className="text-lg font-semibold text-white mb-2">How to Use</h4>
                <ol className="list-decimal list-inside space-y-2 ml-4">
                  <li>Navigate to Technical Analysis from the main menu</li>
                  <li>Select a cryptocurrency symbol</li>
                  <li>Choose your preferred timeframe</li>
                  <li>Review the indicators and signals</li>
                  <li>Export the analysis report if needed</li>
                </ol>
              </div>
            </div>
          </div>
        );

      case 'onchain-sentiment':
        return (
          <div className="space-y-4">
            <h3 className="text-2xl font-semibold text-white mb-4">On-Chain & Sentiment Analysis</h3>
            <div className="space-y-3 text-slate-300">
              <p>The On-Chain & Sentiment Analysis combines blockchain metrics with market sentiment to provide comprehensive insights:</p>
              
              <div className="bg-slate-800 rounded-lg p-4 mt-4">
                <h4 className="text-lg font-semibold text-white mb-2">On-Chain Metrics</h4>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong>Active Addresses:</strong> Number of unique addresses active on the blockchain</li>
                  <li><strong>Transaction Count:</strong> Total number of transactions processed</li>
                  <li><strong>Hash Rate:</strong> Network security and mining power (for PoW coins)</li>
                  <li><strong>TVL (Total Value Locked):</strong> Value locked in DeFi protocols</li>
                  <li><strong>NVT Ratio:</strong> Network Value to Transactions ratio (market cap/volume)</li>
                  <li><strong>MVRV:</strong> Market Value to Realized Value ratio</li>
                  <li><strong>Whale Activity:</strong> Large transaction movements</li>
                  <li><strong>Exchange Flows:</strong> Inflow/outflow from exchanges</li>
                </ul>
              </div>

              <div className="bg-slate-800 rounded-lg p-4 mt-4">
                <h4 className="text-lg font-semibold text-white mb-2">Sentiment Analysis</h4>
                <p className="mb-2">Sentiment data is collected from multiple sources:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong>Reddit:</strong> Posts and comments from cryptocurrency subreddits</li>
                  <li><strong>CryptoPanic:</strong> News and social media posts about cryptocurrencies</li>
                  <li><strong>NewsAPI:</strong> Recent news articles from major news sources</li>
                </ul>
                <p className="mt-3">Sentiment is analyzed using VADER (NLTK) to determine:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong>Sentiment Label:</strong> Positive, Negative, or Neutral</li>
                  <li><strong>Confidence Score:</strong> Strength of the sentiment (0-1)</li>
                  <li><strong>Source Breakdown:</strong> Number of items from each data source</li>
                </ul>
              </div>

              <div className="bg-slate-800 rounded-lg p-4 mt-4">
                <h4 className="text-lg font-semibold text-white mb-2">Final Score & Signal</h4>
                <p className="mb-2">The analysis combines on-chain metrics (75% weight) and sentiment (25% weight) to generate:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong>Final Score:</strong> Weighted combination of both metrics (0-1 scale)</li>
                  <li><strong>Trading Signal:</strong> STRONG_BUY, BUY, NEUTRAL, or SELL</li>
                  <li><strong>Contribution Breakdown:</strong> Shows how much each component contributed</li>
                </ul>
              </div>

              <div className="bg-slate-800 rounded-lg p-4 mt-4">
                <h4 className="text-lg font-semibold text-white mb-2">How to Use</h4>
                <ol className="list-decimal list-inside space-y-2 ml-4">
                  <li>Navigate to On-Chain & Sentiment Analysis from the Analysis Selector</li>
                  <li>Enter a cryptocurrency symbol (e.g., BTC, ETH, SOL)</li>
                  <li>Review the on-chain metrics dashboard</li>
                  <li>Check the sentiment analysis with source breakdown</li>
                  <li>Review the final score and trading signal</li>
                  <li>Export the analysis report if needed</li>
                </ol>
              </div>

              <div className="bg-slate-800 rounded-lg p-4 mt-4">
                <h4 className="text-lg font-semibold text-white mb-2">Requirements</h4>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Valid cryptocurrency symbol (e.g., BTC, ETH, SOL, BNB)</li>
                  <li>Some metrics may be limited for certain cryptocurrencies</li>
                  <li><strong>Tip:</strong> Try popular cryptocurrencies like BTC, ETH, SOL, or BNB for best results</li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 'lstm-prediction':
        return (
          <div className="space-y-4">
            <h3 className="text-2xl font-semibold text-white mb-4">LSTM Predictions</h3>
            <div className="space-y-3 text-slate-300">
              <p>LSTM (Long Short-Term Memory) predictions use AI to forecast future prices:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>Model Information:</strong> View training status, lookback window, and data points</li>
                <li><strong>Performance Metrics:</strong> RMSE, MAPE, and R² score</li>
                <li><strong>Future Predictions:</strong> Price forecasts for upcoming days</li>
                <li><strong>Change Percentage:</strong> Expected price change from current price</li>
              </ul>
              <div className="bg-slate-800 rounded-lg p-4 mt-4">
                <h4 className="text-lg font-semibold text-white mb-2">Understanding Predictions</h4>
                <p className="mb-2">Predictions are based on historical patterns and should be used as one of many factors in decision-making.</p>
                <p>Always consider multiple indicators and market conditions before making trading decisions.</p>
              </div>
            </div>
          </div>
        );

      case 'export':
        return (
          <div className="space-y-4">
            <h3 className="text-2xl font-semibold text-white mb-4">Export Options</h3>
            <div className="space-y-3 text-slate-300">
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">CSV Export</h4>
                <p>Export historical data to CSV format for use in Excel, Google Sheets, or other analysis tools.</p>
                <p className="mt-2">Includes: Date, Symbol, Exchange, OHLCV values, Volume, and Number of Trades</p>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">PDF Export</h4>
                <p>Export charts as high-quality PDF files for reports or presentations.</p>
                <p className="mt-2">Includes: All visible charts in their current chart type (Candlestick/Line/Bar)</p>
              </div>
              <div className="bg-slate-800 rounded-lg p-4 mt-4">
                <h4 className="text-lg font-semibold text-white mb-2">How to Export</h4>
                <ol className="list-decimal list-inside space-y-2 ml-4">
                  <li>Navigate to the page with data you want to export</li>
                  <li>Select your preferred chart types</li>
                  <li>Click the "Export CSV" button for data export</li>
                  <li>Click the "Export Charts PDF" button for chart export</li>
                  <li>Files will download automatically</li>
                </ol>
              </div>
            </div>
          </div>
        );

      case 'troubleshooting':
        return (
          <div className="space-y-4">
            <h3 className="text-2xl font-semibold text-white mb-4">Troubleshooting</h3>
            <div className="space-y-4 text-slate-300">
              <div className="bg-slate-800 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-2">No Data Available</h4>
                <p>If you see "No data available" messages:</p>
                <ul className="list-disc list-inside space-y-1 ml-4 mt-2">
                  <li>Check that you've selected a valid cryptocurrency symbol</li>
                  <li>Verify your date range is correct</li>
                  <li>Try a different exchange filter</li>
                </ul>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-2">Charts Not Loading</h4>
                <p>If charts don't appear:</p>
                <ul className="list-disc list-inside space-y-1 ml-4 mt-2">
                  <li>Refresh the page</li>
                  <li>Check your internet connection</li>
                  <li>Try selecting a different chart type</li>
                </ul>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-2">Export Not Working</h4>
                <p>If exports fail:</p>
                <ul className="list-disc list-inside space-y-1 ml-4 mt-2">
                  <li>Ensure you have data loaded on the page</li>
                  <li>Check browser pop-up blockers</li>
                  <li>Verify you have sufficient disk space</li>
                  <li>Try a different browser if issues persist</li>
                </ul>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="bg-slate-800 rounded-lg shadow-lg">
        <div className="p-6 border-b border-slate-700">
          <h1 className="text-3xl font-bold text-white">Help & Documentation</h1>
          <p className="text-slate-400 mt-2">Comprehensive guide to using Crypto Analyzer</p>
        </div>

        <div className="flex flex-col lg:flex-row">
          {/* Sidebar Navigation */}
          <div className="lg:w-64 bg-slate-900 p-4 border-r border-slate-700">
            <nav className="space-y-2">
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full text-left px-4 py-2 rounded-md transition-colors ${
                    activeSection === section.id
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  {section.title}
                </button>
              ))}
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1 p-6">
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Help;

