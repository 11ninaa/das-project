"""
Module for fetching cryptocurrency OHLCV data from PostgreSQL,
providing historical data for technical analysis and LSTM models in a pandas DataFrame
"""

import logging
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Tuple

import asyncpg
import pandas as pd

try:
    from .config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DEFAULT_QUOTE_ASSET, DEFAULT_SOURCE
except ImportError:
    from shared.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DEFAULT_QUOTE_ASSET, DEFAULT_SOURCE

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Fetches cryptocurrency OHLCV data from PostgreSQL for use in technical
    analysis and LSTM models, managing database interactions via a connection pool.
    """

    TIMEFRAME_DAYS = {
        "1d": 1,
        "1w": 7,
        "1m": 30,
    }
    MIN_DAYS_FOR_INDICATORS = {
        "default": 250,
        "weekly": 120,
        "monthly": 450,
    }

    def __init__(self, db_pool: asyncpg.Pool):

        self.pool = db_pool
        logger.debug("DataFetcher initialized")

    async def fetch_ohlcv_data(
            self,
            symbol: str,
            quote_asset: Optional[str] = None,
            source: str = DEFAULT_SOURCE,
            days: Optional[int] = None,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
            auto_detect_quote: bool = True
    ) -> pd.DataFrame:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data from database.

        Fetches historical price data for a specific cryptocurrency symbol.
        Can specify either number of days or date range.

        """
        symbol = symbol.upper().strip()
        source = source.lower().strip()

        if quote_asset is None or auto_detect_quote:
            if quote_asset is None:
                detected_quote = await self.get_best_quote_asset(symbol, source)
                if detected_quote:
                    quote_asset = detected_quote
                    logger.info(f"Auto-detected quote asset '{quote_asset}' for {symbol}")
                else:
                    quote_asset = DEFAULT_QUOTE_ASSET
            else:
                quote_asset_upper = quote_asset.upper().strip()
                available_quotes = await self.find_available_quote_assets(symbol, source)
                if quote_asset_upper not in available_quotes and available_quotes:
                    quote_asset = await self.get_best_quote_asset(symbol, source)
                    logger.warning(
                        f"Quote asset '{quote_asset_upper}' not available for {symbol}. "
                        f"Using '{quote_asset}' instead. Available: {available_quotes}"
                    )
                elif not available_quotes:
                    raise ValueError(
                        f"No data found for {symbol} in any quote asset from {source}"
                    )
                else:
                    quote_asset = quote_asset_upper
        else:
            quote_asset = quote_asset.upper().strip()

        if end_date is None:
            end_date = date.today()

        if start_date is None:
            if days is None:
                days = self.MIN_DAYS_FOR_INDICATORS["default"]
            start_date = end_date - timedelta(days=days)

        if start_date > end_date:
            start_date = end_date - timedelta(days=1)

        logger.info(
            f"Fetching OHLCV data: {symbol}{quote_asset} from {source}, "
            f"date range: {start_date} to {end_date}"
        )

        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT 
                        date,
                        open,
                        high,
                        low,
                        close,
                        volume,
                        quote_volume,
                        number_of_trades,
                        base_asset,
                        symbol
                    FROM crypto_prices
                    WHERE symbol = $1
                        AND quote_asset = $2
                        AND source = $3
                        AND date::DATE >= $4::DATE
                        AND date::DATE <= $5::DATE
                    ORDER BY date ASC
                """

                rows = await conn.fetch(
                    query,
                    symbol,
                    quote_asset,
                    source,
                    start_date,
                    end_date
                )
        except asyncpg.exceptions.UndefinedTableError:
            logger.error(
                "Table 'crypto_prices' does not exist. Run crypto_etl/main.py to populate the database.")
            raise ValueError("Database table 'crypto_prices' does not exist. Please run the ETL pipeline first.")
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise

        if not rows:
            raise ValueError(
                f"No data found for {symbol}{quote_asset} from {source} "
                f"in date range {start_date} to {end_date}"
            )

        data = {
            'date': [row['date'] for row in rows],
            'open': [float(row['open']) if row['open'] is not None else None for row in rows],
            'high': [float(row['high']) if row['high'] is not None else None for row in rows],
            'low': [float(row['low']) if row['low'] is not None else None for row in rows],
            'close': [float(row['close']) if row['close'] is not None else None for row in rows],
            'volume': [float(row['volume']) if row['volume'] is not None else None for row in rows],
            'quote_volume': [float(row['quote_volume']) if row['quote_volume'] is not None else None for row in rows],
            'number_of_trades': [int(row['number_of_trades']) if row['number_of_trades'] is not None else None for row in rows]
        }

        if rows:
            data['symbol'] = [row.get('symbol', f"{symbol}{quote_asset}") for row in rows]
            data['base_asset'] = [row.get('base_asset', symbol) for row in rows]
            data['quote_asset'] = [quote_asset] * len(rows)

        df = pd.DataFrame(data)

        if df.empty:
            raise ValueError(f"No data returned for {symbol}{quote_asset}")

        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])

        df = df.sort_values('date').reset_index(drop=True)

        df = df.drop_duplicates(subset=['date'], keep='last')

        logger.info(f"Successfully fetched {len(df)} rows of data")
        logger.debug(f"Date range: {df['date'].min()} to {df['date'].max()}")

        return df

    async def fetch_all_available_data(
            self,
            symbol: str,
            quote_asset: Optional[str] = None,
            source: str = DEFAULT_SOURCE,
            auto_detect_quote: bool = True
    ) -> pd.DataFrame:
        """
        Fetches all available historical OHLCV data for a cryptocurrency symbol from the database,
         with optional source and auto-detected quote asset, returning a pandas DataFrame.
        """
        symbol = symbol.upper().strip()
        source = source.lower().strip()

        if quote_asset is None or auto_detect_quote:
            if quote_asset is None:
                detected_quote = await self.get_best_quote_asset(symbol, source)
                if detected_quote:
                    quote_asset = detected_quote
                    logger.info(f"Auto-detected quote asset '{quote_asset}' for {symbol}")
                else:
                    available_all = await self.find_available_quote_assets(symbol, source)
                    raise ValueError(
                        f"No data found for {symbol} in any quote asset from {source}. "
                        f"Available quote assets: {available_all if available_all else 'none'}. "
                        f"Check if symbol exists in database."
                    )
            else:
                quote_asset_upper = quote_asset.upper().strip()
                available_quotes = await self.find_available_quote_assets(symbol, source)
                if quote_asset_upper not in available_quotes and available_quotes:
                    quote_asset = await self.get_best_quote_asset(symbol, source)
                    logger.warning(
                        f"Quote asset '{quote_asset_upper}' not available for {symbol}. "
                        f"Using '{quote_asset}' instead. Available: {available_quotes}"
                    )
                elif not available_quotes:
                    raise ValueError(
                        f"No data found for {symbol} in any quote asset from {source}. "
                        f"Check if symbol exists in database."
                    )
                else:
                    quote_asset = quote_asset_upper
        else:
            quote_asset = quote_asset.upper().strip()

        logger.info(f"Fetching ALL available data for {symbol}{quote_asset} from {source}")

        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT 
                        date,
                        open,
                        high,
                        low,
                        close,
                        volume,
                        quote_volume,
                        number_of_trades,
                        base_asset,
                        symbol
                    FROM crypto_prices
                    WHERE symbol = $1
                        AND quote_asset = $2
                        AND source = $3
                    ORDER BY date ASC
                """

                rows = await conn.fetch(query, symbol, quote_asset, source)

        except asyncpg.exceptions.UndefinedTableError:
            logger.error(
                "Table 'crypto_prices' does not exist. Run crypto_etl/main.py to populate the database.")
            raise ValueError("Database table 'crypto_prices' does not exist. Please run the ETL pipeline first.")
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise

        if not rows:
            available_quotes = await self.find_available_quote_assets(symbol, source)
            if available_quotes:
                raise ValueError(
                    f"No data found for {symbol}{quote_asset} from {source}. "
                    f"However, {symbol} exists with quote assets: {available_quotes}."
                )
            else:
                raise ValueError(
                    f"No data found for {symbol}{quote_asset} from {source}. "
                    f"Symbol {symbol} does not exist in database with any quote asset."
                )

        data = {
            'date': [row['date'] for row in rows],
            'open': [float(row['open']) if row['open'] is not None else None for row in rows],
            'high': [float(row['high']) if row['high'] is not None else None for row in rows],
            'low': [float(row['low']) if row['low'] is not None else None for row in rows],
            'close': [float(row['close']) if row['close'] is not None else None for row in rows],
            'volume': [float(row['volume']) if row['volume'] is not None else None for row in rows],
            'quote_volume': [float(row['quote_volume']) if row['quote_volume'] is not None else None for row in rows],
            'number_of_trades': [int(row['number_of_trades']) if row['number_of_trades'] is not None else None for row in rows],
        }

        if rows:
            data['symbol'] = [row.get('symbol', f"{symbol}{quote_asset}") for row in rows]
            data['base_asset'] = [row.get('base_asset', symbol) for row in rows]
            data['quote_asset'] = [quote_asset] * len(rows)

        df = pd.DataFrame(data)

        if df.empty:
            raise ValueError(f"No data returned for {symbol}{quote_asset}")

        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])

        df = df.sort_values('date').reset_index(drop=True)
        df = df.drop_duplicates(subset=['date'], keep='last')

        logger.info(f"Fetched ALL available data: {len(df)} days for {symbol}{quote_asset}")
        if len(df) > 0:
            logger.debug(f"Date range: {df['date'].min()} to {df['date'].max()}")

        return df

    async def fetch_for_timeframe(
            self,
            symbol: str,
            timeframe: str = "1m",
            quote_asset: Optional[str] = None,
            source: str = DEFAULT_SOURCE,
            minimum_days: Optional[int] = None,
            auto_detect_quote: bool = True
    ) -> pd.DataFrame:
        """
        Fetches OHLCV data for a specific timeframe, auto-detecting quote asset
         and ensuring enough history for indicators, returning a pandas DataFrame.
        """
        if timeframe not in self.TIMEFRAME_DAYS:
            valid_timeframes = ", ".join(self.TIMEFRAME_DAYS.keys())
            raise ValueError(f"Invalid timeframe '{timeframe}'. Valid options: {valid_timeframes}")

        if minimum_days is None:
            if timeframe == "1m":
                minimum_days = self.MIN_DAYS_FOR_INDICATORS.get("monthly", 450)
            elif timeframe == "1w":
                minimum_days = self.MIN_DAYS_FOR_INDICATORS.get("weekly", 120)
            else:  # 1d
                minimum_days = self.MIN_DAYS_FOR_INDICATORS["default"]

        logger.debug(f"Fetching {minimum_days} days for {timeframe} timeframe")

        df = await self.fetch_ohlcv_data(
            symbol=symbol,
            quote_asset=quote_asset,
            source=source,
            days=minimum_days,
            auto_detect_quote=auto_detect_quote
        )

        timeframe_days = self.TIMEFRAME_DAYS[timeframe]
        logger.info(
            f"Fetched {len(df)} days of data for {timeframe} timeframe analysis"
        )

        return df

    async def find_available_quote_assets(
            self,
            symbol: str,
            source: str = DEFAULT_SOURCE,
            preferred_order: Optional[list[str]] = None
    ) -> list[str]:
        """
        Finds all available quote assets for a cryptocurrency symbol from the database,
        optionally prioritizing a preferred order.
        """
        symbol = symbol.upper().strip()
        source = source.lower().strip()

        if preferred_order is None:
            preferred_order = ["USDT", "USDC", "USD", "BUSD"]

        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT DISTINCT quote_asset
                    FROM crypto_prices
                    WHERE symbol = $1
                        AND source = $2
                    ORDER BY quote_asset
                """

                rows = await conn.fetch(query, symbol, source)
                available = [row['quote_asset'] for row in rows]

                if preferred_order:
                    sorted_available = []
                    for preferred in preferred_order:
                        if preferred.upper() in available:
                            sorted_available.append(preferred.upper())
                    for quote in available:
                        if quote not in sorted_available:
                            sorted_available.append(quote)
                    return sorted_available

                return available

        except Exception as e:
            logger.error(f"Failed to find available quote assets for {symbol}: {e}")
            return []

    async def get_best_quote_asset(
            self,
            symbol: str,
            source: str = DEFAULT_SOURCE,
            preferred_order: Optional[list[str]] = None
    ) -> Optional[str]:
        """
        Returns the best available quote asset for a cryptocurrency symbol,
        preferring USDT > USDC > USD, or None if unavailable.
        """
        available = await self.find_available_quote_assets(symbol, source, preferred_order)
        if available:
            return available[0]
        return None

    async def check_data_availability(
            self,
            symbol: str,
            quote_asset: str = DEFAULT_QUOTE_ASSET,
            source: str = DEFAULT_SOURCE
    ) -> Dict[str, any]:
        """
        Returns the available date range for a cryptocurrency symbol,
        including first/last date, total days, and availability status.
        """
        symbol = symbol.upper().strip()
        quote_asset = quote_asset.upper().strip()
        source = source.lower().strip()

        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT 
                        MIN(date::DATE) as first_date,
                        MAX(date::DATE) as last_date,
                        COUNT(*) as total_days
                    FROM crypto_prices
                    WHERE symbol = $1
                        AND quote_asset = $2
                        AND source = $3
                """

                row = await conn.fetchrow(query, symbol, quote_asset, source)

                if row and row['total_days'] > 0:
                    return {
                        'first_date': row['first_date'],
                        'last_date': row['last_date'],
                        'total_days': row['total_days'],
                        'is_available': True
                    }
                else:
                    return {
                        'first_date': None,
                        'last_date': None,
                        'total_days': 0,
                        'is_available': False
                    }

        except Exception as e:
            logger.error(f"Failed to check data availability for {symbol}{quote_asset}: {e}")
            return {
                'first_date': None,
                'last_date': None,
                'total_days': 0,
                'is_available': False
            }

    def validate_dataframe(self, df: pd.DataFrame, min_rows: int = 1) -> bool:
        """
        Validate that DataFrame has required structure for technical analysis.
        """
        if df.empty:
            raise ValueError("DataFrame is empty")

        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"DataFrame missing required columns: {missing_columns}")

        if len(df) < min_rows:
            raise ValueError(
                f"DataFrame must have at least {min_rows} rows of data, "
                f"but got {len(df)} rows. Fetch more historical data."
            )

        critical_columns = ['close']
        for col in critical_columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                logger.warning(f"DataFrame has {null_count} null values in '{col}' column")

        if not df['date'].is_monotonic_increasing:
            logger.warning("DataFrame dates are not in chronological order")

        return True

    @staticmethod
    async def create_connection_pool(
            host: str = DB_HOST,
            port: int = DB_PORT,
            user: str = DB_USER,
            password: str = DB_PASSWORD,
            database: str = DB_NAME,
            min_size: int = 1,
            max_size: int = 10
    ) -> asyncpg.Pool:

        logger.info(f"Creating database connection pool: {user}@{host}:{port}/{database}")

        try:
            pool = await asyncpg.create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                min_size=min_size,
                max_size=max_size
            )
            async with pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                logger.info(f"Connected! PostgreSQL version: {version.split(',')[0]}")
            return pool
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            logger.error("Make sure PostgreSQL is running and credentials are correct!")
            raise

