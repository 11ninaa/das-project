import axios from 'axios';
import { normalizePageResponse, normalizeStockPrice, normalizeStockPrices } from '../utils/dataNormalizer';

/**
 * Base URL for the backend API, configurable via VITE_API_BASE_URL, defaulting to http://localhost:8080.
 */
const API_BASE_URL = 'https://crypto-analyzer-appservice-aac7c4gze8axechj.polandcentral-01.azurewebsites.net';;

/**
 * Axios instance configured with base URL and default headers
 * Used for all API requests to the backend
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Searches crypto assets by exact symbol match (single or comma-separated), returning paginated results in a normalized format.
 */
export const searchCrypto = async (query, page = 0, size = 20) => {
  try {
    const params = { page, size };
    if (query && query.trim().length > 0) {
      params.symbol = query.trim();
    }
    
    const response = await api.get('/api/crypto/search', { params });
    return normalizePageResponse(response.data);
  } catch (error) {
    console.error('Error searching crypto:', error);
    throw error;
  }
};

/**
 * Fetches all crypto prices with pagination by calling the search endpoint without a symbol filter.
 */
export const getAllCrypto = async (page = 0, size = 20) => {
  return searchCrypto(null, page, size);
};

/**
 * Encodes crypto symbols for URL paths, converting special characters (e.g., "BTC/USD" → "BTC%2FUSD").
 */
const encodeSymbol = (symbol) => {
  return encodeURIComponent(symbol);
};

/**
 * Fetches crypto data for a specific symbol and optional date, returning a normalized StockPrice object or array.
 */
export const getCryptoByDate = async (symbol, date) => {
  try {
    const encodedSymbol = encodeSymbol(symbol);
    const response = await api.get(`/api/crypto/${encodedSymbol}`, {
      params: { date },
    });
    const data = response.data;
    if (Array.isArray(data)) {
      return normalizeStockPrices(data);
    }
    return normalizeStockPrice(data);
  } catch (error) {
    if (error.response?.status !== 404) {
      console.error('Error fetching crypto by date:', error);
    }
    throw error;
  }
};

/**
 * Fetches historical crypto data for a symbol over a date range,
 * optionally filtered by exchange, returning an array of StockPrice objects.
 */
export const getCryptoHistory = async (symbol, fromDate, toDate, source = null) => {
  try {
    const encodedSymbol = encodeSymbol(symbol);
    const params = { from: fromDate, to: toDate };
    if (source) params.source = source;
    
    const response = await api.get(`/api/crypto/${encodedSymbol}/history`, { params });
    
    const data = Array.isArray(response.data) ? response.data : (response.data?.content || []);
    return normalizeStockPrices(data);
  } catch (error) {
    if (error.response?.status !== 404) {
      console.error('Error fetching crypto history:', error);
    }
    throw error;
  }
};

/**
 * Fetches all available exchanges/sources,
 * returning an array of unique names with fallback handling if the endpoint is unavailable.
 */
export const getExchanges = async () => {
  try {
    const response = await api.get('/api/crypto/exchanges');
    const data = response.data;
    return Array.isArray(data) ? data : [];
  } catch (error) {
    if (error.response?.status === 404) {
      try {
        const pageResponse = await searchCrypto(null, 0, 100);
        const data = pageResponse.content || [];
        const uniqueSources = [...new Set(data.map(item => item.source).filter(Boolean))];
        return uniqueSources;
      } catch (fallbackError) {
        return [];
      }
    }
    return [];
  }
};

/**
 * Fetches trending or most active crypto assets up to a specified limit,
 * returning formatted asset objects with fallback handling if the endpoint is unavailable.
 */
export const getTrendingAssets = async (limit = 10) => {
  try {
    const response = await api.get('/api/crypto/trending', {
      params: { limit },
    });
    
    const data = Array.isArray(response.data) ? response.data : [];
    const normalized = normalizeStockPrices(data);
    
    const uniqueSymbols = [...new Set(normalized.map(item => item.symbol).filter(Boolean))];
    
    return uniqueSymbols.slice(0, limit).map(symbol => {
      const item = normalized.find(d => d.symbol === symbol);
      return {
        symbol: symbol,
        base_asset: item?.base_asset || symbol.split('/')[0] || '',
        quote_asset: item?.quote_asset || symbol.split('/')[1] || 'USD',
        source: item?.source,
      };
    });
  } catch (error) {
    if (error.response?.status === 404) {
      try {
        const pageResponse = await searchCrypto(null, 0, limit * 3);
        const data = pageResponse.content || [];
        
        const uniqueSymbols = [...new Set(data.map(item => item.symbol).filter(Boolean))];
        
        return uniqueSymbols.slice(0, limit).map(symbol => {
          const item = data.find(d => d.symbol === symbol);
          return {
            symbol: symbol,
            base_asset: item?.base_asset || symbol.split('/')[0] || '',
            quote_asset: item?.quote_asset || symbol.split('/')[1] || 'USD',
            source: item?.source,
          };
        });
      } catch (fallbackError) {
        return [];
      }
    }
    return [];
  }
};

export default api;

/**
 * Fetches technical analysis for a crypto symbol over a specified timeframe, returning signals and indicators.
 */
export const getTechnicalAnalysis = async (symbol, timeframe = "1d") => {
  try {
    const response = await api.get(`/api/analysis/technical/${symbol}`, {
      params: { timeframe },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching technical analysis:', error);
    throw error;
  }
};

/**
 * Get LSTM price predictions
 */
export const getLSTMPrediction = async (symbol, daysAhead = 7) => {
  try {
    const response = await api.get(`/api/analysis/lstm/${symbol}`, {
      params: { daysAhead }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching LSTM prediction:', error);
    throw error;
  }
};

/**
 * Get on-chain and sentiment analysis
 * Backend endpoint: GET /api/analysis/onchain-sentiment/{symbol}
 */
export const getOnChainSentiment = async (symbol) => {
  try {
    const response = await api.get(`/api/analysis/onchain-sentiment/${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching on-chain sentiment analysis:', error);
    throw error;
  }
};

/**
 * Trigger data ingestion/ETL pipeline
 * Backend endpoint: POST /api/etl/trigger
 * Manually triggers the ETL pipeline to update crypto data from exchanges
 */
export const triggerDataUpdate = async () => {
  try {
    const response = await api.post('/api/etl/trigger');
    return response.data;
  } catch (error) {
    console.error('Error triggering data update:', error);
    throw error;
  }
};

/**
 * Get ETL service status
 * Backend endpoint: GET /api/etl/status
 */
export const getETLStatus = async () => {
  try {
    const response = await api.get('/api/etl/status');
    return response.data;
  } catch (error) {
    console.error('Error fetching ETL status:', error);
    throw error;
  }
};