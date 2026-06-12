"""
This adapter handles communication with the CoinGecko API to fetch
market data such as market cap, volume, and price information.
"""

from typing import Dict, Any, Optional
from .api_adapter import APIAdapter


class CoinGeckoAdapter(APIAdapter):
    """
    Adapter for fetching market data from CoinGecko, including price, market cap, volume, and price changes.
    """
    
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3/coins"
    
    COIN_ID_MAP = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "BNB": "binancecoin",
        "ADA": "cardano",
        "XRP": "ripple",
        "DOGE": "dogecoin",
        "DOT": "polkadot",
        "MATIC": "matic-network",
        "AVAX": "avalanche-2",
        "LTC": "litecoin",
        "ETC": "ethereum-classic"
    }
    
    def __init__(self):
        super().__init__(self.COINGECKO_BASE_URL, timeout=10)
    
    def _get_coin_id(self, symbol: str) -> Optional[str]:

        return self.COIN_ID_MAP.get(symbol.upper())
    
    def fetch_data(self, symbol: str, **kwargs) -> Dict[str, Any]:

        coin_id = self._get_coin_id(symbol)
        if not coin_id:
            return {}
        
        url = f"{self.base_url}/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false"
        }
        
        return self._safe_fetch(url, params=params)
    
    def extract_market_data(self, data: Dict[str, Any]) -> Dict[str, float]:

        if not isinstance(data, dict):
            return {}
        if "market_data" not in data:
            return {}
        
        market_data = data["market_data"]
        if not isinstance(market_data, dict):
            return {}
        
        return {
            "market_cap": float(market_data.get("market_cap", {}).get("usd", 0.0) or 0.0),
            "total_volume": float(market_data.get("total_volume", {}).get("usd", 0.0) or 0.0),
            "current_price": float(market_data.get("current_price", {}).get("usd", 0.0) or 0.0),
            "price_change_7d": float(market_data.get("price_change_percentage_7d", 0) or 0)
        }
    
    def calculate_nvt(self, market_cap: float, total_volume: float) -> float:
        """
        Calculate NVT (Network Value to Transactions) ratio.

        """
        if total_volume > 0:
            return market_cap / total_volume
        return 0.0
    
    def estimate_mvrv(self, price_change_7d: float) -> float:
        """
        This is an approximation based on price change, as real MVRV
        requires on-chain data that's not easily available.


        """
        mvrv = 1.5 + (price_change_7d / 100.0) * 0.5
        return max(0.5, min(3.0, mvrv))



