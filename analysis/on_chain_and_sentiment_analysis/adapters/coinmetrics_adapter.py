"""
This adapter handles communication with the CoinMetrics API to fetch
on-chain metrics such as active addresses, transaction counts, and hash rate.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from .api_adapter import APIAdapter


class CoinMetricsAdapter(APIAdapter):
    
    COINMETRICS_BASE_URL = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
    
    def __init__(self):
        super().__init__(self.COINMETRICS_BASE_URL, timeout=10)
    
    def fetch_data(self, symbol: str, metrics: Optional[str] = None, 
                   days: int = 7, **kwargs) -> Dict[str, Any]:

        if metrics is None:
            metrics = "AdrActCnt,TxCnt,CapMktUSD"
        
        end_time = datetime.now().strftime("%Y-%m-%d")
        start_time = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        asset_symbol = symbol.lower()
        
        params = {
            "assets": asset_symbol,
            "metrics": metrics,
            "start_time": start_time,
            "end_time": end_time
        }
        
        return self._safe_fetch(self.base_url, params=params)
    
    def fetch_hash_rate(self, symbol: str, days: int = 7) -> Dict[str, Any]:

        end_time = datetime.now().strftime("%Y-%m-%d")
        start_time = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        url = f"{self.base_url}?assets={symbol.lower()}&metrics=HashRate&start_time={start_time}&end_time={end_time}"
        return self._safe_fetch(url)
    
    def extract_latest_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:

        if not isinstance(data, dict):
            return {}
        if not data.get("data") or len(data["data"]) == 0:
            return {}
        
        latest = data["data"][-1]
        if not isinstance(latest, dict):
            return {}
        
        return {
            "addresses": float(latest.get("AdrActCnt", 0) or 0),
            "transactions": float(latest.get("TxCnt", 0) or 0),
            "market_cap": float(latest.get("CapMktUSD", 0) or 0),
            "hash_rate": float(latest.get("HashRate", 0) or 0)
        }



