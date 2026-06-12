/**
 * Provides helper functions to safely access OHLCV data from stock price items,
 * handling both nested and flat formats and defaulting missing values to 0.
 */
export const getOHLCV = (item) => {
  if (!item) return { open: 0, high: 0, low: 0, close: 0, volume: 0 };

  if (item.ohlcv && typeof item.ohlcv === 'object') {
    return {
      open: item.ohlcv.open || item.open || 0,
      high: item.ohlcv.high || item.high || 0,
      low: item.ohlcv.low || item.low || 0,
      close: item.ohlcv.close || item.close || 0,
      volume: item.ohlcv.volume || item.volume || 0,
    };
  }

  return {
    open: item.open || 0,
    high: item.high || 0,
    low: item.low || 0,
    close: item.close || 0,
    volume: item.volume || 0,
  };
};

/**
 * Extract the opening price from a stock price item
 */
export const getOpen = (item) => getOHLCV(item).open;

/**
 * Extract the highest price from a stock price item
 */
export const getHigh = (item) => getOHLCV(item).high;

/**
 * Extract the lowest price from a stock price item

 */
export const getLow = (item) => getOHLCV(item).low;

/**
 * Extract the closing price from a stock price item

 */
export const getClose = (item) => getOHLCV(item).close;

/**
 * Extract the trading volume from a stock price item

 */
export const getVolume = (item) => getOHLCV(item).volume;

