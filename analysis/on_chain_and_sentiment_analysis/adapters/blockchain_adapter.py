"""
Adapter for fetching Bitcoin hash rate data from the Blockchain.com API.
"""

from typing import Dict, Any, Optional
from .api_adapter import APIAdapter


class BlockchainAdapter(APIAdapter):
    """
    Adapter for fetching Bitcoin hash rate data from the unauthenticated Blockchain.com API.
    """
    
    BLOCKCHAIN_BASE_URL = "https://blockchain.info/q/hashrate"
    
    HASHES_TO_TERAHASH = 1e12
    
    def __init__(self):
        super().__init__(self.BLOCKCHAIN_BASE_URL, timeout=10)
    
    def fetch_data(self, symbol: str, **kwargs) -> Dict[str, Any]:
        """
        Fetches Bitcoin hash rate data from Blockchain.com, ignoring extra parameters and returning it as a dictionary.
        """
        if symbol.upper() != "BTC":
            return {}
        
        try:
            response = self.session.get(self.base_url, timeout=self.timeout)
            if response.status_code == 200:
                hash_rate_str = response.text.strip()
                if hash_rate_str:
                    try:
                        hash_rate_hs = float(hash_rate_str)
                        if hash_rate_hs > 0:
                            hash_rate_th = hash_rate_hs / self.HASHES_TO_TERAHASH
                            return {"hash_rate": hash_rate_th}
                    except (ValueError, TypeError):
                        cleaned = ''.join(
                            c for c in hash_rate_str 
                            if c.isdigit() or c == '.' or c.lower() in 'e+-'
                        )
                        if cleaned:
                            try:
                                hash_rate_hs = float(cleaned)
                                if hash_rate_hs > 0:
                                    hash_rate_th = hash_rate_hs / self.HASHES_TO_TERAHASH
                                    return {"hash_rate": hash_rate_th}
                            except ValueError:
                                pass
        except Exception:
            pass
        
        return {}
    
    def extract_hash_rate(self, data: Dict[str, Any]) -> float:
        """
        Extracts the hash rate in TH/s from Blockchain.com API response, returning 0.0 if unavailable.
        """
        if not isinstance(data, dict):
            return 0.0
        return float(data.get("hash_rate", 0.0) or 0.0)



