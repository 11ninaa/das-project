"""
Database configuration for crypto_etl module.
"""

import os

# # Database connection settings
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_PORT = int(os.getenv("DB_PORT", "5431"))
# DB_USER = os.getenv("DB_USER", "postgres")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
# DB_NAME = os.getenv("DB_NAME", "example_db")





DB_HOST = os.getenv("DB_HOST", "das-db-2025-nm.postgres.database.azure.com")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "ninaanak")
DB_PASSWORD = os.getenv("DB_PASSWORD", "BandWidth/compuTe")
DB_NAME = os.getenv("DB_NAME", "example_das")












