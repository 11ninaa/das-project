"""

This module provides adapters for external APIs using the Adapter Pattern.
Each adapter abstracts the details of communicating with a specific external service.
"""

from .api_adapter import APIAdapter
from .coinmetrics_adapter import CoinMetricsAdapter
from .coingecko_adapter import CoinGeckoAdapter
from .defillama_adapter import DefiLlamaAdapter
from .blockchain_adapter import BlockchainAdapter

__all__ = [
    'APIAdapter',
    'CoinMetricsAdapter',
    'CoinGeckoAdapter',
    'DefiLlamaAdapter',
    'BlockchainAdapter'
]

