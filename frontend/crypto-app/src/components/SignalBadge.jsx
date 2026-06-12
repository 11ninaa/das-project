
function SignalBadge({ signal, confidence, reasoning }) {
  const colors = {
    BUY: 'bg-green-500 hover:bg-green-600',
    STRONG_BUY: 'bg-green-600 hover:bg-green-700',
    SELL: 'bg-red-500 hover:bg-red-600',
    HOLD: 'bg-yellow-500 hover:bg-yellow-600',
    NEUTRAL: 'bg-yellow-500 hover:bg-yellow-600'
  };

  const textColors = {
    BUY: 'text-green-700',
    STRONG_BUY: 'text-green-800',
    SELL: 'text-red-700',
    HOLD: 'text-yellow-700',
    NEUTRAL: 'text-yellow-700'
  };

  return (
    <div className="my-6 p-6 border-2 border-slate-600 rounded-lg bg-slate-800 shadow-lg">
      <div className="flex items-center gap-6 mb-3">
        <button className={`px-6 py-3 rounded-lg text-white font-bold text-xl shadow-md transition-colors ${colors[signal] || 'bg-gray-500'}`}>
          {signal || 'HOLD'}
        </button>
        <div className="flex-1">
          <div className="text-2xl font-semibold text-white">
            Confidence: <span className={textColors[signal] || 'text-slate-300'}>{(confidence * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>
      {reasoning && (
        <p className="mt-3 text-slate-300 text-sm bg-slate-700 p-3 rounded border border-slate-600">
          {reasoning}
        </p>
      )}
    </div>
  );
}

export default SignalBadge;