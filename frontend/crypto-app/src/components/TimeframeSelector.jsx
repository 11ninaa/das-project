
function TimeframeSelector({ timeframe, onChange }) {
  const timeframes = [
    { value: '1d', label: 'Daily' },
    { value: '1w', label: 'Weekly' },
    { value: '1m', label: 'Monthly' }
  ];

  return (
    <div className="flex gap-2 mb-6">
      {timeframes.map(tf => (
        <button
          key={tf.value}
          onClick={() => onChange(tf.value)}
          className={`px-4 py-2 rounded transition-colors ${
            timeframe === tf.value 
              ? 'bg-blue-600 text-white font-semibold' 
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          {tf.label}
        </button>
      ))}
    </div>
  );
}

export default TimeframeSelector;