
function TechnicalIndicators({ indicators, votes }) {
  if (!indicators) {
    return <div className="p-4 text-slate-300">No indicator data available</div>;
  }

  const safeGet = (obj, path, defaultValue = null) => {
    try {
      const keys = path.split('.');
      let value = obj;
      for (const key of keys) {
        value = value?.[key];
        if (value === undefined || value === null) return defaultValue;
      }
      return value;
    } catch {
      return defaultValue;
    }
  };

  return (
    <div className="space-y-4 mt-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 border border-slate-600 rounded-lg bg-slate-800">
          <h3 className="font-bold text-xl mb-4 text-white border-b border-slate-600 pb-2">Oscillators</h3>
          <div className="space-y-4">
            {safeGet(indicators, 'rsi.value') !== null && (
              <div className="bg-slate-700 rounded p-3 border-l-4 border-blue-500">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-white">RSI (Relative Strength Index)</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    safeGet(indicators, 'rsi.signal') === 'BUY' ? 'bg-green-600 text-white' :
                    safeGet(indicators, 'rsi.signal') === 'SELL' ? 'bg-red-600 text-white' :
                    'bg-slate-600 text-slate-300'
                  }`}>
                    {safeGet(indicators, 'rsi.signal', 'NEUTRAL')}
                  </span>
                </div>
                <p className="text-lg font-bold text-slate-200">{safeGet(indicators, 'rsi.value').toFixed(2)}</p>
                <p className="text-xs text-slate-400 mt-1">Range: 0-100 (Oversold: &lt;30, Overbought: &gt;70)</p>
              </div>
            )}
            
            {safeGet(indicators, 'macd.macd_line') !== null && (
              <div className="bg-slate-700 rounded p-3 border-l-4 border-purple-500">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-white">MACD (Moving Average Convergence Divergence)</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    safeGet(indicators, 'macd.signal') === 'BUY' ? 'bg-green-600 text-white' :
                    safeGet(indicators, 'macd.signal') === 'SELL' ? 'bg-red-600 text-white' :
                    'bg-slate-600 text-slate-300'
                  }`}>
                    {safeGet(indicators, 'macd.signal', 'NEUTRAL')}
                  </span>
                </div>
                <div className="space-y-1 text-sm">
                  <p className="text-slate-300">
                    <span className="text-slate-400">MACD Line:</span> 
                    <span className="ml-2 font-semibold text-white">{safeGet(indicators, 'macd.macd_line').toFixed(6)}</span>
                  </p>
                  <p className="text-slate-300">
                    <span className="text-slate-400">Signal Line:</span> 
                    <span className="ml-2 font-semibold text-white">{safeGet(indicators, 'macd.signal_line', 0).toFixed(6)}</span>
                  </p>
                  <p className="text-slate-300">
                    <span className="text-slate-400">Histogram:</span> 
                    <span className={`ml-2 font-semibold ${
                      safeGet(indicators, 'macd.histogram', 0) > 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {safeGet(indicators, 'macd.histogram', 0).toFixed(6)}
                    </span>
                  </p>
                </div>
              </div>
            )}
            
            {safeGet(indicators, 'stochastic.k') !== null && (
              <div className="bg-slate-700 rounded p-3 border-l-4 border-yellow-500">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-white">Stochastic Oscillator</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    safeGet(indicators, 'stochastic.signal') === 'BUY' ? 'bg-green-600 text-white' :
                    safeGet(indicators, 'stochastic.signal') === 'SELL' ? 'bg-red-600 text-white' :
                    'bg-slate-600 text-slate-300'
                  }`}>
                    {safeGet(indicators, 'stochastic.signal', 'NEUTRAL')}
                  </span>
                </div>
                <div className="space-y-1 text-sm">
                  <p className="text-slate-300">
                    <span className="text-slate-400">%K (Fast):</span> 
                    <span className="ml-2 font-semibold text-white">{safeGet(indicators, 'stochastic.k').toFixed(2)}</span>
                  </p>
                  <p className="text-slate-300">
                    <span className="text-slate-400">%D (Slow):</span> 
                    <span className="ml-2 font-semibold text-white">{safeGet(indicators, 'stochastic.d').toFixed(2)}</span>
                  </p>
                  <p className="text-xs text-slate-400 mt-1">Range: 0-100 (Oversold: &lt;20, Overbought: &gt;80)</p>
                </div>
              </div>
            )}
            
            {safeGet(indicators, 'adx.value') !== null && (
              <div className="bg-slate-700 rounded p-3 border-l-4 border-orange-500">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-white">ADX (Average Directional Index)</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    safeGet(indicators, 'adx.signal') === 'STRONG_TREND' ? 'bg-green-600 text-white' :
                    safeGet(indicators, 'adx.signal') === 'WEAK_TREND' ? 'bg-red-600 text-white' :
                    'bg-slate-600 text-slate-300'
                  }`}>
                    {safeGet(indicators, 'adx.signal', 'MODERATE_TREND').replace('_', ' ')}
                  </span>
                </div>
                <p className="text-lg font-bold text-slate-200">{safeGet(indicators, 'adx.value').toFixed(2)}</p>
                <p className="text-xs text-slate-400 mt-1">Measures trend strength (Strong: &gt;25, Weak: &lt;20)</p>
              </div>
            )}
            
            {safeGet(indicators, 'cci.value') !== null && (
              <div className="bg-slate-700 rounded p-3 border-l-4 border-cyan-500">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-white">CCI (Commodity Channel Index)</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    safeGet(indicators, 'cci.signal') === 'BUY' ? 'bg-green-600 text-white' :
                    safeGet(indicators, 'cci.signal') === 'SELL' ? 'bg-red-600 text-white' :
                    'bg-slate-600 text-slate-300'
                  }`}>
                    {safeGet(indicators, 'cci.signal', 'NEUTRAL')}
                  </span>
                </div>
                <p className="text-lg font-bold text-slate-200">{safeGet(indicators, 'cci.value').toFixed(2)}</p>
                <p className="text-xs text-slate-400 mt-1">Oversold: &lt;-100, Overbought: &gt;100</p>
              </div>
            )}
          </div>
        </div>
        
        <div className="p-5 border border-slate-600 rounded-lg bg-slate-800">
          <h3 className="font-bold text-xl mb-4 text-white border-b border-slate-600 pb-2">Moving Averages</h3>
          <div className="space-y-4">
            {/* SMA */}
            {safeGet(indicators, 'sma.value') !== null && (
              <div className="bg-slate-700 rounded p-3 border-l-4 border-blue-400">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-white">SMA (Simple Moving Average)</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    safeGet(indicators, 'sma.signal') === 'BUY' ? 'bg-green-600 text-white' :
                    safeGet(indicators, 'sma.signal') === 'SELL' ? 'bg-red-600 text-white' :
                    'bg-slate-600 text-slate-300'
                  }`}>
                    {safeGet(indicators, 'sma.signal', 'NEUTRAL')}
                  </span>
                </div>
                <p className="text-lg font-bold text-slate-200">{safeGet(indicators, 'sma.value').toFixed(2)}</p>
                {safeGet(indicators, 'sma.price_vs_sma_percent') !== null && (
                  <p className={`text-sm mt-1 font-semibold ${
                    safeGet(indicators, 'sma.price_vs_sma_percent') > 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    Price vs SMA: {safeGet(indicators, 'sma.price_vs_sma_percent') > 0 ? '+' : ''}
                    {safeGet(indicators, 'sma.price_vs_sma_percent').toFixed(2)}%
                  </p>
                )}
              </div>
            )}
            
            {safeGet(indicators, 'ema.value') !== null && (
              <div className="bg-slate-700 rounded p-3 border-l-4 border-purple-400">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-white">EMA (Exponential Moving Average)</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    safeGet(indicators, 'ema.signal') === 'BUY' ? 'bg-green-600 text-white' :
                    safeGet(indicators, 'ema.signal') === 'SELL' ? 'bg-red-600 text-white' :
                    'bg-slate-600 text-slate-300'
                  }`}>
                    {safeGet(indicators, 'ema.signal', 'NEUTRAL')}
                  </span>
                </div>
                <p className="text-lg font-bold text-slate-200">{safeGet(indicators, 'ema.value').toFixed(2)}</p>
                {safeGet(indicators, 'ema.price_vs_ema_percent') !== null && (
                  <p className={`text-sm mt-1 font-semibold ${
                    safeGet(indicators, 'ema.price_vs_ema_percent') > 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    Price vs EMA: {safeGet(indicators, 'ema.price_vs_ema_percent') > 0 ? '+' : ''}
                    {safeGet(indicators, 'ema.price_vs_ema_percent').toFixed(2)}%
                  </p>
                )}
              </div>
            )}
            
            {safeGet(indicators, 'wma.value') !== null && (
              <div className="bg-slate-700 rounded p-3 border-l-4 border-yellow-400">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-white">WMA (Weighted Moving Average)</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    safeGet(indicators, 'wma.signal') === 'BUY' ? 'bg-green-600 text-white' :
                    safeGet(indicators, 'wma.signal') === 'SELL' ? 'bg-red-600 text-white' :
                    'bg-slate-600 text-slate-300'
                  }`}>
                    {safeGet(indicators, 'wma.signal', 'NEUTRAL')}
                  </span>
                </div>
                <p className="text-lg font-bold text-slate-200">{safeGet(indicators, 'wma.value').toFixed(2)}</p>
                {safeGet(indicators, 'wma.price_vs_wma_percent') !== null && (
                  <p className={`text-sm mt-1 font-semibold ${
                    safeGet(indicators, 'wma.price_vs_wma_percent') > 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    Price vs WMA: {safeGet(indicators, 'wma.price_vs_wma_percent') > 0 ? '+' : ''}
                    {safeGet(indicators, 'wma.price_vs_wma_percent').toFixed(2)}%
                  </p>
                )}
              </div>
            )}
            
            {safeGet(indicators, 'bollinger_bands.upper') !== null && (
              <div className="bg-slate-700 rounded p-3 border-l-4 border-orange-400">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-white">Bollinger Bands</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    safeGet(indicators, 'bollinger_bands.signal') === 'BUY' ? 'bg-green-600 text-white' :
                    safeGet(indicators, 'bollinger_bands.signal') === 'SELL' ? 'bg-red-600 text-white' :
                    'bg-slate-600 text-slate-300'
                  }`}>
                    {safeGet(indicators, 'bollinger_bands.signal', 'NEUTRAL')}
                  </span>
                </div>
                <div className="space-y-1 text-sm">
                  <p className="text-slate-300">
                    <span className="text-slate-400">Upper Band:</span> 
                    <span className="ml-2 font-semibold text-red-300">{safeGet(indicators, 'bollinger_bands.upper').toFixed(2)}</span>
                  </p>
                  <p className="text-slate-300">
                    <span className="text-slate-400">Middle Band (SMA):</span> 
                    <span className="ml-2 font-semibold text-white">{safeGet(indicators, 'bollinger_bands.middle').toFixed(2)}</span>
                  </p>
                  <p className="text-slate-300">
                    <span className="text-slate-400">Lower Band:</span> 
                    <span className="ml-2 font-semibold text-green-300">{safeGet(indicators, 'bollinger_bands.lower').toFixed(2)}</span>
                  </p>
                  <p className="text-xs text-slate-400 mt-2">Bands show price volatility (2 standard deviations)</p>
                </div>
              </div>
            )}
            
            {safeGet(indicators, 'volume_ma.volume_ratio') !== null && (
              <div className="bg-slate-700 rounded p-3 border-l-4 border-cyan-400">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-white">Volume Moving Average</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    safeGet(indicators, 'volume_ma.signal') === 'HIGH_VOLUME' ? 'bg-green-600 text-white' :
                    safeGet(indicators, 'volume_ma.signal') === 'LOW_VOLUME' ? 'bg-red-600 text-white' :
                    'bg-slate-600 text-slate-300'
                  }`}>
                    {safeGet(indicators, 'volume_ma.signal', 'NORMAL_VOLUME').replace('_', ' ')}
                  </span>
                </div>
                <p className="text-lg font-bold text-slate-200">
                  {safeGet(indicators, 'volume_ma.volume_ratio').toFixed(2)}x
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  Current volume / Average volume (High: &gt;1.2x, Low: &lt;0.8x)
                </p>
                {safeGet(indicators, 'volume_ma.current_volume') !== null && (
                  <p className="text-xs text-slate-300 mt-1">
                    Current: {safeGet(indicators, 'volume_ma.current_volume').toLocaleString()} | 
                    Average: {safeGet(indicators, 'volume_ma.value').toLocaleString()}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
      
      <div className="p-5 border border-slate-600 rounded-lg bg-slate-800">
        <h3 className="font-bold text-xl mb-3 text-white border-b border-slate-600 pb-2">Signal Votes Summary</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-green-900/30 rounded p-4 border border-green-600/50 text-center">
            <div className="text-3xl font-bold text-green-400">{votes.buy || 0}</div>
            <div className="text-sm text-green-300 mt-1">Buy Votes</div>
          </div>
          <div className="bg-red-900/30 rounded p-4 border border-red-600/50 text-center">
            <div className="text-3xl font-bold text-red-400">{votes.sell || 0}</div>
            <div className="text-sm text-red-300 mt-1">Sell Votes</div>
          </div>
          <div className="bg-slate-700 rounded p-4 border border-slate-600 text-center">
            <div className="text-3xl font-bold text-slate-400">{votes.neutral || 0}</div>
            <div className="text-sm text-slate-300 mt-1">Neutral Votes</div>
          </div>
        </div>
        <div className="mt-4 text-center text-sm text-slate-400">
          Total Indicators: {(votes.buy || 0) + (votes.sell || 0) + (votes.neutral || 0)}
        </div>
      </div>
    </div>
  );
}

export default TechnicalIndicators;