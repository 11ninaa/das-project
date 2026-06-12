"""
This module provides database configuration constants used across
all analysis modules that need to connect to the database.
"""

import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5433"))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "crypto_db")

DEFAULT_QUOTE_ASSET = "USDT"
DEFAULT_SOURCE = "binance"
DEFAULT_MIN_DAYS = 250

