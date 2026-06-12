# DataFetcher has been moved to shared folder
# Import from shared for backward compatibility
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.data_fetcher import DataFetcher

__all__ = ['DataFetcher']

