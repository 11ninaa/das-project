"""
This module fetches raw on-chain metrics from various external APIs.
It uses the Adapter Pattern to abstract away the details of different APIs.
"""

from typing import Dict, Any, Optional
import os
from adapters import (
    CoinMetricsAdapter,
    CoinGeckoAdapter,
    DefiLlamaAdapter,
    BlockchainAdapter
)


class OnChainFetcher:
    """
    Fetches raw on-chain metrics via adapters for multiple APIs, providing a consistent
     interface with easier swapping, testing, and error handling.
    """
    
    POW_COINS = ["BTC", "LTC", "DOGE", "ETC", "BCH", "BSV", "DASH", "ZEC"]
    
    SYMBOL_ESTIMATES = {
        "BTC": {"addresses": 900_000, "transactions": 300_000},
        "ETH": {"addresses": 500_000, "transactions": 1_000_000},
        "SOL": {"addresses": 200_000, "transactions": 50_000_000},
        "BNB": {"addresses": 100_000, "transactions": 3_000_000},
        "ADA": {"addresses": 50_000, "transactions": 100_000},
        "XRP": {"addresses": 40_000, "transactions": 1_000_000},
        "DOGE": {"addresses": 80_000, "transactions": 30_000},
        "DOT": {"addresses": 20_000, "transactions": 50_000},
        "MATIC": {"addresses": 150_000, "transactions": 2_000_000},
        "AVAX": {"addresses": 30_000, "transactions": 500_000},
        "LTC": {"addresses": 100_000, "transactions": 50_000},
    }
    
    def __init__(self, symbol: str):

        self.symbol = symbol.upper()
        
        self.coinmetrics_adapter = CoinMetricsAdapter()
        self.coingecko_adapter = CoinGeckoAdapter()
        self.defillama_adapter = DefiLlamaAdapter()
        self.blockchain_adapter = BlockchainAdapter()


    def get_activity(self) -> Dict[str, float]:

        hash_rate = self.get_hash_rate()
        
        coinmetrics_data = self.coinmetrics_adapter.fetch_data(self.symbol)
        metrics = self.coinmetrics_adapter.extract_latest_metrics(coinmetrics_data)
        
        if isinstance(metrics, dict) and metrics and (metrics.get("addresses", 0) > 0 or metrics.get("transactions", 0) > 0):
            return {
                "addresses": metrics.get("addresses", 0.0),
                "transactions": metrics.get("transactions", 0.0),
                "market_cap": metrics.get("market_cap", 0.0),
                "hash_rate": hash_rate
            }
        
        return self._get_activity_fallback(hash_rate)

    def _get_activity_fallback(self, hash_rate: float) -> Dict[str, float]:

        if self.symbol in self.SYMBOL_ESTIMATES:
            estimates = self.SYMBOL_ESTIMATES[self.symbol]
            estimated_addresses = estimates["addresses"]
            estimated_transactions = estimates["transactions"]
        else:
            estimated_addresses = 10_000
            estimated_transactions = 5_000
        
        market_cap = 0.0
        
        coingecko_data = self.coingecko_adapter.fetch_data(self.symbol)
        market_data = self.coingecko_adapter.extract_market_data(coingecko_data)
        
        if market_data and isinstance(market_data, dict):
            market_cap = market_data.get("market_cap", 0.0)
            
            if market_cap > 0:
                btc_market_cap = 800_000_000_000
                if btc_market_cap > 0:
                    scale_factor = min(2.0, max(0.01, market_cap / btc_market_cap))
                    estimated_addresses = max(5000, int(estimated_addresses * scale_factor))
                    estimated_transactions = max(1000, int(estimated_transactions * scale_factor))
        
        return {
            "addresses": float(estimated_addresses),
            "transactions": float(estimated_transactions),
            "market_cap": market_cap,
            "hash_rate": hash_rate
        }

    def get_hash_rate(self) -> float:
        """
        Uses Blockchain.com API for BTC, CoinMetrics for other PoW coins.
        Returns hash rate in TH/s (terahash per second) for consistency.
        Returns 0.0 for PoS coins (not applicable).

        """
        if self.symbol == "BTC":
            # Use Blockchain.com API (using adapter)
            blockchain_data = self.blockchain_adapter.fetch_data(self.symbol)
            hash_rate = self.blockchain_adapter.extract_hash_rate(blockchain_data)
            if hash_rate > 0:
                return hash_rate
        
        if self.symbol in self.POW_COINS:
            coinmetrics_data = self.coinmetrics_adapter.fetch_hash_rate(self.symbol)
            metrics = self.coinmetrics_adapter.extract_latest_metrics(coinmetrics_data)
            hash_rate = metrics.get("hash_rate", 0.0) if isinstance(metrics, dict) else 0.0
            
            if hash_rate > 0:
                if hash_rate > 1e10:  # Likely in H/s
                    return hash_rate / 1e12
                return hash_rate
        
        return 0.0

    def get_tvl(self) -> float:

        defillama_data = self.defillama_adapter.fetch_data(self.symbol)
        return self.defillama_adapter.extract_tvl(defillama_data)

    def get_nvt_mvrv(self) -> Dict[str, float]:
        """
        NVT is calculated from CoinGecko market data.
        MVRV is approximated using price change (real MVRV requires on-chain data).

        """
        coingecko_data = self.coingecko_adapter.fetch_data(self.symbol)
        market_data = self.coingecko_adapter.extract_market_data(coingecko_data)
        
        if not market_data or not isinstance(market_data, dict):
            return {"nvt": 0.0, "mvrv": 1.5}
        
        market_cap = market_data.get("market_cap", 0.0)
        total_volume = market_data.get("total_volume", 0.0)
        price_change_7d = market_data.get("price_change_7d", 0.0)
        
        nvt = self.coingecko_adapter.calculate_nvt(market_cap, total_volume)
        
        mvrv = self.coingecko_adapter.estimate_mvrv(price_change_7d)
        
        return {
            "nvt": nvt,
            "mvrv": mvrv
        }

    def get_exchange_flows(self) -> Dict[str, Any]:
        """
        Get exchange flows (inflow/outflow from exchanges).
        This typically requires premium APIs, but we'll provide structure.
        """

        return {
            "data": [{
                "netflow": 0.0,
                "inflow": 0.0,
                "outflow": 0.0,
                "note": "Exchange flows require premium API access (Glassnode, CoinMetrics Pro) or tracking known exchange addresses"
            }]
        }

    def get_all_metrics(self) -> Dict[str, Any]:

        activity = self.get_activity()
        nvt_mvrv = self.get_nvt_mvrv()
        tvl = self.get_tvl()
        exchange_flows = self.get_exchange_flows()
        
        return {
            "AdrActCnt": activity["addresses"],
            "TxCnt": activity["transactions"],
            "HashRate": activity["hash_rate"],
            "tvl": tvl,
            "nvt": nvt_mvrv["nvt"],
            "mvrv": nvt_mvrv["mvrv"],
            "exchange_flow": exchange_flows
        }