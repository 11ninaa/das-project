"""
Database schema SQL reference.

This file contains the database schema SQL for reference purposes.

"""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS crypto_prices (
    symbol TEXT NOT NULL,
    base_asset TEXT,
    quote_asset TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'binance',
    date DATE NOT NULL,
    open NUMERIC(20, 10),
    high NUMERIC(20, 10),
    low NUMERIC(20, 10),
    close NUMERIC(20, 10),
    volume NUMERIC(30, 10),
    quote_volume NUMERIC(30, 10),
    number_of_trades INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (symbol, quote_asset, date)
);

CREATE INDEX IF NOT EXISTS idx_crypto_prices_date ON crypto_prices (date DESC);
CREATE INDEX IF NOT EXISTS idx_crypto_prices_symbol ON crypto_prices (symbol);
CREATE INDEX IF NOT EXISTS idx_crypto_prices_source ON crypto_prices (source);
"""

























