"""
This module defines the abstract base class for all API adapters using the Adapter Pattern.
Each concrete adapter implements this interface to provide a consistent way to interact
with external APIs.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests


class APIAdapter(ABC):
    """
    Abstract base class defining a consistent interface for API adapters, enabling easy swapping,
    testing, and unified error handling.
    """
    
    def __init__(self, base_url: str, timeout: int = 10):

        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _safe_fetch(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code != 200:
                if response.status_code == 404:
                    return {}
                elif response.status_code == 429:
                    return {}
                elif response.status_code >= 500:
                    return {}
                return {}
            
            if response.text.strip():
                try:
                    return response.json()
                except ValueError:
                    return {"value": response.text.strip()}
            
            return {}
            
        except requests.exceptions.Timeout:
            return {}
        except requests.exceptions.RequestException:
            return {}
        except Exception:
            return {}
    
    @abstractmethod
    def fetch_data(self, symbol: str, **kwargs) -> Dict[str, Any]:

        pass



