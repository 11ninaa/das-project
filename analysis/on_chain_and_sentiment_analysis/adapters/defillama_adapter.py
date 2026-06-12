"""

This adapter handles communication with the DefiLlama API to fetch
Total Value Locked (TVL) data for cryptocurrencies.
"""

from typing import Dict, Any
from .api_adapter import APIAdapter


class DefiLlamaAdapter(APIAdapter):
    """
    This adapter fetches TVL (Total Value Locked) data from DefiLlama.
    DefiLlama returns TVL as a plain number, not JSON.
    """

    DEFILLAMA_BASE_URL = "https://api.llama.fi/v2"

    def __init__(self):
        super().__init__(self.DEFILLAMA_BASE_URL, timeout=10)

    def fetch_data(self, symbol: str, **kwargs) -> Dict[str, Any]:

        chain_map = {
            "BTC": ["Bitcoin", "bitcoin"],
            "ETH": ["Ethereum", "ethereum"],
            "SOL": ["Solana", "solana"],
            "BNB": ["Binance", "binance"],
            "ADA": ["Cardano", "cardano"],
            "XRP": ["XRP", "xrp"],
            "AVAX": ["Avalanche", "avalanche"],
            "DOT": ["Polkadot", "polkadot"],
            "MATIC": ["Polygon", "polygon"],
            "LTC": ["Litecoin", "litecoin"]
        }

        chain_names = chain_map.get(symbol.upper())
        if not chain_names:
            return {}

        url = f"{self.base_url}/chains"
        response = self._safe_fetch(url)

        if not response:
            return {}

        chains = None
        if isinstance(response, list):
            chains = response
        elif isinstance(response, dict):
            if "chains" in response:
                chains = response["chains"]
            elif "data" in response:
                chains = response["data"]
            else:
                for key, value in response.items():
                    if isinstance(value, list):
                        chains = value
                        break

        if not chains or not isinstance(chains, list):
            return self._try_chain_specific_endpoint(symbol)

        for chain in chains:
            if not isinstance(chain, dict):
                continue
            
            chain_name = chain.get("name", "")
            token_symbol = chain.get("tokenSymbol", "")
            chain_gecko_id = chain.get("gecko_id", "")
            tvl = chain.get("tvl", 0.0)
            
            if tvl is None or tvl == 0:
                continue
            
            if token_symbol and token_symbol.upper() == symbol.upper():
                return {"value": float(tvl)}
            
            for target_name in chain_names:
                if chain_name and chain_name.lower() == target_name.lower():
                    return {"value": float(tvl)}
            
            for target_name in chain_names:
                if chain_gecko_id and chain_gecko_id.lower() == target_name.lower():
                    return {"value": float(tvl)}

        return self._try_chain_specific_endpoint(symbol)
    
    def _try_chain_specific_endpoint(self, symbol: str) -> Dict[str, Any]:
        """
        Attempts to fetch TVL for a cryptocurrency using a chain-specific endpoint,
        returning a dictionary or empty if unavailable.
        """
        chain_slug_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "BNB": "binance",
            "ADA": "cardano",
            "XRP": "xrp",
            "AVAX": "avalanche",
            "DOT": "polkadot",
            "MATIC": "polygon",
            "LTC": "litecoin"
        }
        
        slug = chain_slug_map.get(symbol.upper())
        if not slug:
            return {}
        
        url = f"{self.base_url}/chain/{slug}"
        response = self._safe_fetch(url)
        
        if response and isinstance(response, dict):
            tvl = response.get("tvl", 0.0)
            if tvl is None:
                tvl = 0.0
            return {"value": float(tvl)}
        
        return {}

    def extract_tvl(self, data: Dict[str, Any]) -> float:

        if not isinstance(data, dict):
            return 0.0
        return float(data.get("value", 0.0) or 0.0)



