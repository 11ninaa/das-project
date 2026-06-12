/**
 * Normalizes a backend StockPrice object for frontend use,
 * creating a nested ohlcv object while preserving original flat fields; returns null if input is missing.
 */
export const normalizeStockPrice = (stockPrice) => {
  if (!stockPrice) return null;

  return {
    ...stockPrice,
    ohlcv: {
      open: stockPrice.open || 0,
      high: stockPrice.high || 0,
      low: stockPrice.low || 0,
      close: stockPrice.close || 0,
      volume: stockPrice.volume || 0,
    },
    id: stockPrice.id,
    symbol: stockPrice.symbol,
    base_asset: stockPrice.base_asset,
    quote_asset: stockPrice.quote_asset,
    source: stockPrice.source,
    date: stockPrice.date,
    open: stockPrice.open,
    high: stockPrice.high,
    low: stockPrice.low,
    close: stockPrice.close,
    volume: stockPrice.volume,
    quote_volume: stockPrice.quote_volume,
    number_of_trades: stockPrice.number_of_trades,
    created_at: stockPrice.created_at,
    updated_at: stockPrice.updated_at,
  };
};

/**
 * Normalizes an array of backend StockPrice objects, filtering out null/undefined entries and returning a normalized array.
 */
export const normalizeStockPrices = (stockPrices) => {
  if (!Array.isArray(stockPrices)) return [];
  return stockPrices.map(normalizeStockPrice).filter(Boolean);
};

/**
 * Normalizes a Spring Data Page response for frontend use, ensuring consistent property names and normalized content array.
 */
export const normalizePageResponse = (pageResponse) => {
  if (!pageResponse) return { content: [], totalElements: 0, totalPages: 0, number: 0, size: 20 };

  return {
    ...pageResponse,
    content: normalizeStockPrices(pageResponse.content || []),
    totalElements: pageResponse.totalElements || 0,
    totalPages: pageResponse.totalPages || 0,
    number: pageResponse.number !== undefined ? pageResponse.number : pageResponse.page || 0,
    size: pageResponse.size || pageResponse.pageSize || 20,
  };
};

