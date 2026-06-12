/**
 * OnChainDashboard Component
 * 
 * Displays all 8 on-chain metrics with their raw and normalized values
 */

function OnChainDashboard({ onchainDetails }) {
  if (!onchainDetails) {
    return null;
  }

  const { raw, normalized, onchain_score } = onchainDetails || {};

  if (!raw || !normalized) {
    return (
      <div className="bg-slate-800 rounded-lg shadow p-6">
        <p className="text-slate-300">On-chain data not available</p>
      </div>
    );
  }

  const metrics = [
    {
      key: 'addresses',
      label: 'Active Addresses',
      rawKey: 'AdrActCnt',
      description: 'Number of unique addresses active on the network'
    },
    {
      key: 'transactions',
      label: 'Transactions',
      rawKey: 'TxCnt',
      description: 'Total number of transactions'
    },
    {
      key: 'hashrate',
      label: 'Hash Rate',
      rawKey: 'HashRate',
      description: 'Network security (PoW blockchains)'
    },
    {
      key: 'tvl',
      label: 'Total Value Locked',
      rawKey: 'tvl',
      description: 'DeFi value locked in protocols'
    },
    {
      key: 'nvt',
      label: 'NVT Ratio',
      rawKey: 'nvt',
      description: 'Market Cap / Transaction Volume',
      inverse: true
    },
    {
      key: 'mvrv',
      label: 'MVRV',
      rawKey: 'mvrv',
      description: 'Market Value to Realized Value',
      inverse: true
    },
    {
      key: 'whale_activity',
      label: 'Whale Activity',
      rawKey: 'whale_movements',
      description: 'Large transaction activity (>$1M)',
      isObject: true
    },
    {
      key: 'exchange_flows',
      label: 'Exchange Flows',
      rawKey: 'exchange_flow',
      description: 'Net flow to/from exchanges',
      isObject: true
    }
  ];

  const formatValue = (value, key) => {
    if (value === null || value === undefined) return 'N/A';
    
    if (key === 'exchange_flow') {
      const netflow = value?.data?.[0]?.netflow;
      if (netflow === undefined || netflow === null) return 'N/A';
      return netflow >= 0 
        ? `+$${formatLargeNumber(netflow)}` 
        : `-$${formatLargeNumber(Math.abs(netflow))}`;
    }

    if (typeof value === 'number') {
      if (key === 'nvt' || key === 'mvrv') {
        return value.toFixed(2);
      }
      return formatLargeNumber(value);
    }
    return value;
  };

  const formatLargeNumber = (num) => {
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toFixed(2);
  };

  const getRawValue = (metric) => {
    if (metric.rawKey === 'exchange_flow') {
      return raw.exchange_flow?.data?.[0]?.netflow || 0;
    }
    if (metric.rawKey === 'whale_movements') {
      const whaleData = raw.whale_movements || {};
      return whaleData.large_transactions_24h || 0;
    }
    return raw[metric.rawKey] || 0;
  };
  
  const getRawValueDisplay = (metric) => {
    if (metric.rawKey === 'whale_movements') {
      const whaleData = raw.whale_movements || {};
      return {
        transactions: whaleData.large_transactions_24h || 0,
        volume: formatLargeNumber(whaleData.total_volume_whales || 0),
        score: ((whaleData.whale_activity_score || 0) * 100).toFixed(1) + '%'
      };
    }
    if (metric.rawKey === 'exchange_flow') {
      const flowData = raw.exchange_flow?.data?.[0] || {};
      return {
        netflow: flowData.netflow || 0,
        inflow: flowData.inflow || 0,
        outflow: flowData.outflow || 0
      };
    }
    return null;
  };

  const getNormalizedValue = (metric) => {
    return normalized[metric.key] || 0;
  };

  const getScoreColor = (normalizedValue, inverse = false) => {
    const score = inverse ? (1 - normalizedValue) : normalizedValue;
    if (score >= 0.7) return 'text-green-400';
    if (score >= 0.4) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="bg-slate-800 rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-white">On-Chain Metrics</h2>
        <div className="text-right">
          <p className="text-sm text-slate-400">Overall Score</p>
          <p className="text-2xl font-bold text-blue-400">
            {(onchain_score * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {metrics.map((metric) => {
          const rawValue = getRawValue(metric);
          const normalizedValue = getNormalizedValue(metric);
          const scoreColor = getScoreColor(normalizedValue, metric.inverse);

          return (
            <div
              key={metric.key}
              className="bg-slate-700 rounded-lg p-4 border border-slate-600 hover:border-blue-500 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="text-sm font-semibold text-white">{metric.label}</h3>
                  <p className="text-xs text-slate-400">{metric.description}</p>
                </div>
              </div>

              <div className="mt-3 space-y-2">
                {metric.isObject ? (
                  // Special display for object metrics (whale movements, exchange flows)
                  <div className="space-y-1">
                    {metric.rawKey === 'whale_movements' && (
                      <>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-slate-400">Large TXs (24h):</span>
                          <span className="text-sm font-medium text-white">
                            {getRawValueDisplay(metric).transactions}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-slate-400">Volume:</span>
                          <span className="text-sm font-medium text-white">
                            ${getRawValueDisplay(metric).volume}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-slate-400">Activity Score:</span>
                          <span className={`text-sm font-bold ${scoreColor}`}>
                            {getRawValueDisplay(metric).score}
                          </span>
                        </div>
                      </>
                    )}
                    {metric.rawKey === 'exchange_flow' && (
                      <>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-slate-400">Net Flow:</span>
                          <span className="text-sm font-medium text-white">
                            ${formatLargeNumber(Math.abs(getRawValueDisplay(metric).netflow))}
                            {getRawValueDisplay(metric).netflow >= 0 ? ' (Inflow)' : ' (Outflow)'}
                          </span>
                        </div>
                        {raw.exchange_flow?.data?.[0]?.note && (
                          <p className="text-xs text-yellow-400 mt-1">
                            {raw.exchange_flow.data[0].note.substring(0, 50)}...
                          </p>
                        )}
                      </>
                    )}
                    <div className="flex justify-between items-center mt-2">
                      <span className="text-xs text-slate-400">Normalized:</span>
                      <span className={`text-sm font-bold ${scoreColor}`}>
                        {(normalizedValue * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ) : (
                  // Standard display for numeric metrics
                  <>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-slate-400">Raw Value:</span>
                      <span className="text-sm font-medium text-white">
                        {formatValue(rawValue, metric.rawKey)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-slate-400">Normalized:</span>
                      <span className={`text-sm font-bold ${scoreColor}`}>
                        {(normalizedValue * 100).toFixed(1)}%
                      </span>
                    </div>
                  </>
                )}
                
                {/* Progress bar */}
                <div className="w-full bg-slate-600 rounded-full h-2 mt-2">
                  <div
                    className={`h-2 rounded-full ${
                      normalizedValue >= 0.7 ? 'bg-green-500' :
                      normalizedValue >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${normalizedValue * 100}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Note about missing metrics */}
      {(raw.exchange_flow?.data?.[0]?.netflow === 0 || 
        (raw.HashRate === 0 && !['BTC', 'LTC', 'ETC'].includes(raw.symbol || '')) ||
        raw.whale_movements?.note) && (
        <div className="mt-4 p-3 bg-yellow-900/30 border border-yellow-700/50 rounded-lg">
          <p className="text-xs text-yellow-300">
            <strong>Note:</strong> Some metrics may show limited data:
            <ul className="list-disc list-inside mt-1 space-y-0.5">
              {raw.exchange_flow?.data?.[0]?.netflow === 0 && (
                <li>Exchange flows require premium API access</li>
              )}
              {raw.HashRate === 0 && !['BTC', 'LTC', 'ETC'].includes(raw.symbol || '') && (
                <li>Hash rate is only applicable to PoW blockchains (BTC, LTC, ETC)</li>
              )}
              {raw.whale_movements?.note && (
                <li>Whale movements: {raw.whale_movements.note}</li>
              )}
            </ul>
          </p>
        </div>
      )}
    </div>
  );
}

export default OnChainDashboard;

