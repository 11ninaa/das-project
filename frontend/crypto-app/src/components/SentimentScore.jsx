/**
 * SentimentScore Component
 * Displays sentiment analysis results including label, confidence, and score
 */

function SentimentScore({ sentiment }) {
  if (!sentiment) {
    return null;
  }

  const { 
    label, 
    confidence, 
    sentiment_score_raw, 
    sentiment_score_norm, 
    source_breakdown, 
    text_length,
    nlp_method,
    textblob_comparison
  } = sentiment;

  const labelColors = {
    positive: 'bg-green-500',
    negative: 'bg-red-500',
    neutral: 'bg-yellow-500'
  };

  const textColors = {
    positive: 'text-green-300',
    negative: 'text-red-300',
    neutral: 'text-yellow-300'
  };

  const labelText = label ? label.charAt(0).toUpperCase() + label.slice(1) : 'Neutral';

  // Calculate percentage for display
  const scorePercent = ((sentiment_score_norm || 0) * 100).toFixed(1);
  const rawScore = (sentiment_score_raw || 0).toFixed(3);

  return (
    <div className="bg-slate-800 rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4 text-white">Sentiment Analysis</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Sentiment Label */}
        <div className="text-center p-4 bg-slate-700 rounded-lg">
          <p className="text-sm text-slate-400 mb-2">Sentiment</p>
          <div className={`inline-block px-4 py-2 rounded-lg text-white font-bold ${labelColors[label] || labelColors.neutral}`}>
            {labelText}
          </div>
        </div>

        {/* Confidence Score */}
        <div className="text-center p-4 bg-slate-700 rounded-lg">
          <p className="text-sm text-slate-400 mb-2">Confidence</p>
          <p className={`text-2xl font-bold ${textColors[label] || textColors.neutral}`}>
            {(confidence * 100).toFixed(1)}%
          </p>
        </div>

        {/* Raw Score */}
        <div className="text-center p-4 bg-slate-700 rounded-lg">
          <p className="text-sm text-slate-400 mb-2">Score</p>
          <p className={`text-2xl font-bold ${textColors[label] || textColors.neutral}`}>
            {rawScore}
          </p>
          <p className="text-xs text-slate-400 mt-1">({scorePercent}% normalized)</p>
        </div>
      </div>

      {/* Score Bar Visualization */}
      <div className="mt-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm text-slate-400">Sentiment Score:</span>
          <span className={`text-sm font-semibold ${textColors[label] || textColors.neutral}`}>
            {rawScore} (Range: -1.0 to +1.0)
          </span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-4 relative overflow-hidden">
          {/* Negative half (red) */}
          <div 
            className="absolute left-0 top-0 h-full bg-red-500"
            style={{ width: sentiment_score_raw < 0 ? `${Math.abs(sentiment_score_raw) * 50}%` : '0%' }}
          />

          <div 
            className="absolute right-0 top-0 h-full bg-green-500"
            style={{ width: sentiment_score_raw > 0 ? `${sentiment_score_raw * 50}%` : '0%' }}
          />
          <div className="absolute left-1/2 top-0 h-full w-0.5 bg-white transform -translate-x-1/2" />
        </div>
        <div className="flex justify-between text-xs text-slate-400 mt-1">
          <span>Negative (-1.0)</span>
          <span>Neutral (0.0)</span>
          <span>Positive (+1.0)</span>
        </div>
      </div>

      {nlp_method && (
        <div className="mt-4 pt-4 border-t border-slate-700">
          <p className="text-xs text-slate-400 text-center">
            NLP Method: <span className="text-blue-400 font-semibold">{nlp_method}</span>
          </p>
        </div>
      )}

      {source_breakdown && (
        <div className="mt-4 pt-4 border-t border-slate-700">
          <h3 className="text-sm font-semibold text-white mb-2">Data Sources</h3>
          <div className="grid grid-cols-3 gap-3 text-xs">
            <div className="text-center p-3 bg-slate-700 rounded">
              <p className="text-slate-400 mb-1">Reddit</p>
              <p className="text-white font-semibold text-lg">{source_breakdown.reddit || 0}</p>
              <p className="text-slate-500 text-[10px] mt-1">Posts/Comments</p>
            </div>
            <div className="text-center p-3 bg-slate-700 rounded">
              <p className="text-slate-400 mb-1">CryptoPanic</p>
              <p className="text-white font-semibold text-lg">{source_breakdown.cryptopanic || 0}</p>
              <p className="text-slate-500 text-[10px] mt-1">News Articles</p>
            </div>
            <div className="text-center p-3 bg-slate-700 rounded">
              <p className="text-slate-400 mb-1">NewsAPI</p>
              <p className="text-white font-semibold text-lg">{source_breakdown.newsapi || 0}</p>
              <p className="text-slate-500 text-[10px] mt-1">
                {source_breakdown.newsapi === 0 ? 'API key needed' : 'News Articles'}
              </p>
            </div>
          </div>
          
          {text_length && (
            <p className="text-xs text-slate-400 mt-3 text-center">
              Analyzed {text_length} characters of text from {Object.values(source_breakdown).reduce((a, b) => a + (b || 0), 0)} sources
            </p>
          )}
        </div>
      )}

      {textblob_comparison && (
        <div className="mt-4 pt-4 border-t border-slate-700">
          <h3 className="text-sm font-semibold text-white mb-2">NLP Method Comparison</h3>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div className="p-2 bg-slate-700 rounded">
              <p className="text-slate-400 mb-1">VADER (NLTK)</p>
              <p className="text-white font-semibold">{label}</p>
              <p className="text-slate-300">{(confidence * 100).toFixed(1)}%</p>
            </div>
            <div className="p-2 bg-slate-700 rounded">
              <p className="text-slate-400 mb-1">TextBlob</p>
              <p className="text-white font-semibold">{textblob_comparison.label}</p>
              <p className="text-slate-300">{(textblob_comparison.confidence * 100).toFixed(1)}%</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SentimentScore;

