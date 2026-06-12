"""
This module normalizes on-chain metrics and calculates an on-chain score.
It uses the Strategy Pattern for normalization methods.
"""

from typing import Dict, Any
from onchain_fetcher import OnChainFetcher
from strategies import (
    LogarithmicNormalizationStrategy,
    InverseNormalizationStrategy
)


class OnChainLogic:

    WEIGHTS = {
        "addresses": 0.15,
        "transactions": 0.10,
        "hashrate": 0.12,
        "tvl": 0.12,
        "nvt": 0.28,
        "mvrv": 0.23,
        "exchange_flows": 0.00
    }

    LIMITS = {
        "AdrActCnt": 1_500_000,
        "TxCnt": 1_000_000,
        "HashRate": 3000.0,
        "tvl": 50_000_000_000,
        "nvt": 150,
        "mvrv": 5.0,
        "exchange_flow": 20_000_000_000
    }

    def __init__(self, symbol: str):

        self.fetcher = OnChainFetcher(symbol)
        self.total_onchain_weight = sum(self.WEIGHTS.values())
        
        self.positive_normalizer = LogarithmicNormalizationStrategy()
        self.inverse_normalizer = InverseNormalizationStrategy()

    def analyze(self) -> Dict[str, Any]:

        raw = self.fetcher.get_all_metrics()

        normalized = {}

        normalized["addresses"] = self.positive_normalizer.normalize(
            raw["AdrActCnt"], self.LIMITS["AdrActCnt"]
        )
        normalized["transactions"] = self.positive_normalizer.normalize(
            raw["TxCnt"], self.LIMITS["TxCnt"]
        )
        normalized["hashrate"] = self.positive_normalizer.normalize(
            raw["HashRate"], self.LIMITS["HashRate"]
        )
        normalized["tvl"] = self.positive_normalizer.normalize(
            raw["tvl"], self.LIMITS["tvl"]
        )

        normalized["nvt"] = self.inverse_normalizer.normalize(
            raw["nvt"], self.LIMITS["nvt"]
        )
        normalized["mvrv"] = self.inverse_normalizer.normalize(
            raw["mvrv"], self.LIMITS["mvrv"]
        )

        exchange_flow = raw.get("exchange_flow", {})
        if isinstance(exchange_flow, dict):
            exchange_flow_data = exchange_flow.get("data", [{}])
            netflow_val = exchange_flow_data[0].get("netflow", 0.0) if exchange_flow_data else 0.0
        else:
            netflow_val = 0.0
        normalized["exchange_flows"] = self.positive_normalizer.normalize(
            abs(netflow_val), self.LIMITS["exchange_flow"]
        )

        onchain_score = (
            normalized["addresses"] * self.WEIGHTS["addresses"] +
            normalized["transactions"] * self.WEIGHTS["transactions"] +
            normalized["hashrate"] * self.WEIGHTS["hashrate"] +
            normalized["tvl"] * self.WEIGHTS["tvl"] +
            normalized["nvt"] * self.WEIGHTS["nvt"] +
            normalized["mvrv"] * self.WEIGHTS["mvrv"]
        ) / self.total_onchain_weight  # Divide by total weight to get [0, 1]

        return {
            "raw": raw,
            "normalized": normalized,
            "onchain_score": round(onchain_score, 4)
        }