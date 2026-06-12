/**
 * CombinedAnalysis Component
 * Displays the combined on-chain + sentiment analysis with final signal
 */

import SignalBadge from './SignalBadge';

function CombinedAnalysis({ decision, onchainScore, sentimentScore }) {
  if (!decision) {
    return null;
  }

  const { final_score, signal, contribution } = decision;

  const signalMap = {
    STRONG_BUY: { color: 'bg-green-600', textColor: 'text-green-300', label: 'STRONG BUY' },
    BUY: { color: 'bg-green-500', textColor: 'text-green-300', label: 'BUY' },
    NEUTRAL: { color: 'bg-yellow-500', textColor: 'text-yellow-300', label: 'NEUTRAL' },
    SELL: { color: 'bg-red-500', textColor: 'text-red-300', label: 'SELL' }
  };

  const signalInfo = signalMap[signal] || signalMap.NEUTRAL;

  return (
    <div className="bg-slate-800 rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4 text-white">Combined Analysis</h2>

      {/* Final Signal */}
      <div className="mb-6">
        <SignalBadge
          signal={signal}
          confidence={final_score}
          reasoning={`Combined score: ${(final_score * 100).toFixed(1)}% (On-chain: ${(contribution.onchain * 100).toFixed(1)}%, Sentiment: ${(contribution.sentiment * 100).toFixed(1)}%)`}
        />
      </div>

      {/* Score Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Final Score */}
        <div className={`text-center p-4 rounded-lg ${signalInfo.color} bg-opacity-20 border-2 ${signalInfo.color} border-opacity-50`}>
          <p className="text-sm text-slate-400 mb-2">Final Score</p>
          <p className={`text-3xl font-bold ${signalInfo.textColor}`}>
            {(final_score * 100).toFixed(1)}%
          </p>
          <p className={`text-lg font-semibold mt-2 ${signalInfo.textColor}`}>
            {signalInfo.label}
          </p>
        </div>

        {/* On-Chain Contribution */}
        <div className="text-center p-4 bg-blue-900/30 border border-blue-700/50 rounded-lg">
          <p className="text-sm text-slate-400 mb-2">On-Chain Contribution</p>
          <p className="text-2xl font-bold text-blue-400">
            {(contribution.onchain * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-slate-400 mt-2">
            Weight: 75%
          </p>
          {onchainScore && (
            <p className="text-xs text-slate-400 mt-1">
              Score: {(onchainScore * 100).toFixed(1)}%
            </p>
          )}
        </div>

        {/* Sentiment Contribution */}
        <div className="text-center p-4 bg-purple-900/30 border border-purple-700/50 rounded-lg">
          <p className="text-sm text-slate-400 mb-2">Sentiment Contribution</p>
          <p className="text-2xl font-bold text-purple-400">
            {(contribution.sentiment * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-slate-400 mt-2">
            Weight: 25%
          </p>
          {sentimentScore && (
            <p className="text-xs text-slate-400 mt-1">
              Score: {(sentimentScore * 100).toFixed(1)}%
            </p>
          )}
        </div>
      </div>

      {/* Weighted Average Explanation */}
      <div className="bg-slate-700 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-white mb-2">How the Score is Calculated</h3>
        <p className="text-xs text-slate-300">
          Final Score = (On-Chain Score × 75%) + (Sentiment Score × 25%)
        </p>
        <p className="text-xs text-slate-400 mt-2">
          The on-chain metrics carry more weight as they reflect actual blockchain activity,
          while sentiment provides additional market psychology insights.
        </p>
      </div>
    </div>
  );
}

export default CombinedAnalysis;

