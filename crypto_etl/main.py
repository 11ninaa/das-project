"""
Crypto ETL Pipeline - Pipe and Filter Architecture

Implements a three-stage pipeline for processing cryptocurrency exchange data:
Filter 1 → Filter 2 → Filter 3
"""

import asyncio
import logging
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from database import create_db_pool, apply_schema
from filters import filter1, filter2, filter3

# Pipeline settings
SYMBOL_LIMIT = 1000
MAX_HISTORICAL_DAYS = 3650
WORKERS = 8  # Number of concurrent downloads
ALLOWED_QUOTES = ["USDT", "USDC", "BUSD", "USD"]

# Binance API settings
BINANCE_BASE_URL = "https://api.binance.com"
BINANCE_RPM = 1200
BINANCE_TIMEOUT = 30

# Retry settings
RETRY_ATTEMPTS = 5
RETRY_MIN_WAIT = 0.5
RETRY_MAX_WAIT = 10


# UTILITY FUNCTIONS


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def utc_midnight(dt: date) -> datetime:
    """Convert date to datetime at midnight UTC."""
    return datetime.combine(dt, datetime.min.time(), tzinfo=timezone.utc)


def to_milliseconds(dt: datetime) -> int:
    """Convert datetime to milliseconds timestamp."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)



# RATE LIMITER


class RateLimiter:
    """Simple rate limiter to avoid hitting API limits."""

    def __init__(self, rate_per_minute: int, burst: int = None):
        self.rate_per_second = rate_per_minute / 60.0
        self.burst = burst or rate_per_minute
        self.tokens = float(self.burst)
        self.last_update = asyncio.get_event_loop().time()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1):
        """Wait if needed to respect rate limits."""
        async with self._lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate_per_second)
            self.last_update = now

            if self.tokens >= tokens:
                self.tokens -= tokens
            else:
                needed = tokens - self.tokens
                wait_time = needed / self.rate_per_second
                await asyncio.sleep(wait_time)
                self.tokens = 0
                self.last_update = asyncio.get_event_loop().time()


rate_limiter = RateLimiter(rate_per_minute=BINANCE_RPM, burst=100)



# DATA MODEL


@dataclass
class PriceRecord:
    """Single day's OHLCV price data for a cryptocurrency."""
    symbol: str
    base_asset: str
    quote_asset: str
    source: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_volume: float
    number_of_trades: int



# BINANCE API FUNCTIONS


async def make_binance_request(
        session: aiohttp.ClientSession,
        url: str,
        params: Optional[Dict[str, Any]] = None,
) -> Any:
    """Make HTTP request to Binance API with retry and rate limiting."""
    retry_policy = AsyncRetrying(
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_exponential(min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True,
    )

    async for attempt in retry_policy:
        with attempt:
            await rate_limiter.acquire()
            async with session.get(url, params=params, timeout=BINANCE_TIMEOUT) as resp:
                if resp.status in {418, 429}:
                    raise aiohttp.ClientResponseError(
                        resp.request_info, resp.history, status=resp.status, message="Rate limited"
                    )
                resp.raise_for_status()
                return await resp.json()


async def download_ohlcv(
        session: aiohttp.ClientSession,
        symbol: str,
        quote_asset: str,
        start_date: date,
        end_date: date,
) -> Optional[List[List[Any]]]:
    """Download historical OHLCV data from Binance."""
    start_ms = to_milliseconds(utc_midnight(start_date))
    end_ms = to_milliseconds(utc_midnight(end_date))

    url = f"{BINANCE_BASE_URL}/api/v3/klines"
    full_symbol = f"{symbol}{quote_asset}"
    collected = []
    query_start = start_ms

    try:
        while query_start <= end_ms:
            params = {
                "symbol": full_symbol,
                "interval": "1d",
                "startTime": query_start,
                "endTime": end_ms,
                "limit": 1000,
            }

            chunk = await make_binance_request(session, url, params=params)
            if not chunk:
                break

            collected.extend(chunk)

            if len(chunk) < 1000:
                break

            last_open = chunk[-1][0]
            next_start = last_open + 1
            if next_start > end_ms:
                break

            query_start = next_start
            await asyncio.sleep(0.01)

        return collected if collected else None

    except aiohttp.ClientResponseError as e:
        if e.status == 400:
            return None
        raise



# TRANSFORM FUNCTIONS


def transform_binance_data(symbol: str, klines: List[List[Any]], quote_asset: str) -> List[PriceRecord]:
    """
    Transform Binance klines data to PriceRecord objects.
    
    Binance klines array indices: [0] open_time, [1] open, [2] high, [3] low,
    [4] close, [5] volume, [7] quote_volume, [8] number_of_trades
    """
    records = []
    for kline in klines:
        open_time = datetime.fromtimestamp(kline[0] / 1000, tz=timezone.utc)
        record = PriceRecord(
            symbol=symbol,
            base_asset=symbol,
            quote_asset=quote_asset,
            source="binance",
            date=open_time,
            open=float(kline[1]),
            high=float(kline[2]),
            low=float(kline[3]),
            close=float(kline[4]),
            volume=float(kline[5]),
            quote_volume=float(kline[7]),
            number_of_trades=int(kline[8]),
        )
        records.append(record)
    return records



# MAIN PIPELINE


async def run_pipeline():
    """Orchestrate the three-stage filter pipeline."""
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("Crypto ETL Pipeline - Pipe and Filter Architecture")
    logger.info("=" * 80)
    logger.info(f"Target: Top {SYMBOL_LIMIT} active cryptocurrencies")
    logger.info(f"Historical data: {MAX_HISTORICAL_DAYS} days (~{MAX_HISTORICAL_DAYS / 365:.1f} years)")
    logger.info(f"Workers: {WORKERS}")
    logger.info("=" * 80)

    pool = None
    try:
        logger.info("Connecting to database...")
        pool = await create_db_pool()
        await apply_schema(pool)

        timeout = aiohttp.ClientTimeout(total=300)
        connector = aiohttp.TCPConnector(limit_per_host=WORKERS * 2)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            start_time = datetime.now(timezone.utc)

            logger.info("")
            logger.info("=" * 80)
            logger.info("FILTER 1: Downloading top active cryptocurrency symbols")
            logger.info("=" * 80)
            symbols = await filter1(session)
            logger.info(f"Filter 1 output: {len(symbols)} symbols ready for Filter 2")

            logger.info("")
            logger.info("=" * 80)
            logger.info("FILTER 2: Checking last date of available data")
            logger.info("=" * 80)
            ranges = await filter2(pool, symbols)
            logger.info(f"Filter 2 output: {len(ranges)} symbols need data updates")

            if not ranges:
                logger.info("All data is up to date! Pipeline complete.")
                return

            logger.info("")
            logger.info("=" * 80)
            logger.info("FILTER 3: Filling in missing data")
            logger.info("=" * 80)
            results = await filter3(session, pool, ranges)

            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            total_rows = sum(r.get("rows", 0) for r in results.values())
            success = sum(1 for r in results.values() if r.get("rows", 0) > 0)
            errors = sum(1 for r in results.values() if r.get("error"))

            logger.info("")
            logger.info("=" * 80)
            logger.info("PIPELINE COMPLETE")
            logger.info("=" * 80)
            logger.info(f"Symbols processed: {len(results)}")
            logger.info(f"Successful: {success}")
            logger.info(f"Errors: {errors}")
            logger.info(f"Total rows inserted: {total_rows}")
            logger.info(f"Time: {elapsed:.2f} seconds ({elapsed / 60:.2f} minutes)")
            logger.info("=" * 80)

    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise
    finally:
        if pool:
            await pool.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    setup_logging()
    try:
        asyncio.run(run_pipeline())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
