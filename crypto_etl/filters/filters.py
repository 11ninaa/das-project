"""
Pipe and Filter Architecture - Filter Implementations

This module implements the three filters of the pipe-and-filter architecture
for processing cryptocurrency exchange data.

Filter 1: Automatically download symbol list of top 1000 active cryptocurrencies
  - Excludes delisted, low liquidity, duplicates, unstable quote currencies
  - Ranks by 24h volume to get most active coins

Filter 2: Check last date of available data
  - For each symbol, checks database to see up to which date data exists
  - Determines what date ranges need to be downloaded (10 years or maximum available)
  - Identifies missing date ranges

Filter 3: Fill in missing data
  - Downloads all missing data up to current date
  - Downloads daily OHLCV data (Open, High, Low, Close, Volume)
  - Includes 24H metrics (Last Price, 24H High, 24H Low, 24H Volume)
  - Includes liquidity indicators (number of trades, quote volume)
  - Transforms and formats data consistently
  - Stores in database with proper formatting

"""

import asyncio
import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

import aiohttp
import asyncpg
from tqdm.asyncio import tqdm

logger = logging.getLogger(__name__)


async def filter1(session: aiohttp.ClientSession) -> List[Dict[str, str]]:
    """
    Download and rank top 1000 active cryptocurrencies by 24h volume.
    Filters out delisted coins, low liquidity pairs, duplicates, and unstable quote currencies.
    Args:
        session: HTTP session for making API requests
    Returns:
        List of dictionaries with keys: symbol, base_asset, quote_asset, source
    """
    # Import here to avoid circular import
    import sys
    import os
    filters_dir = os.path.dirname(os.path.abspath(__file__))
    crypto_etl_dir = os.path.dirname(filters_dir)
    if crypto_etl_dir in sys.path:
        sys.path.remove(crypto_etl_dir)
    sys.path.insert(0, crypto_etl_dir)
    from main import ALLOWED_QUOTES, BINANCE_BASE_URL, SYMBOL_LIMIT, make_binance_request
    
    logger.info("Filter 1: Fetching and ranking top active cryptocurrencies...")
    
    url = f"{BINANCE_BASE_URL}/api/v3/exchangeInfo"
    data = await make_binance_request(session, url)
    symbols = data.get("symbols", [])
    
    logger.info("Filter 1: Fetching 24h volume data to rank cryptocurrencies...")
    ticker_url = f"{BINANCE_BASE_URL}/api/v3/ticker/24hr"
    tickers = await make_binance_request(session, ticker_url)
    
    volume_map = {ticker.get("symbol", ""): float(ticker.get("quoteVolume", 0)) for ticker in tickers}
    
    symbol_candidates = []
    seen_symbols = set()
    MIN_24H_VOLUME = 10000
    
    for s in symbols:
        if s.get("status") != "TRADING":
            continue
        
        symbol = s["symbol"]
        
        for quote in ALLOWED_QUOTES:
            if symbol.endswith(quote):
                base = symbol.replace(quote, "")
                symbol_key = base.upper()
                
                if symbol_key in seen_symbols:
                    break
                
                quote_volume = volume_map.get(symbol, 0)
                if quote_volume < MIN_24H_VOLUME:
                    break
                
                seen_symbols.add(symbol_key)
                symbol_candidates.append({
                    "symbol": symbol_key,
                    "base_asset": base,
                    "quote_asset": quote,
                    "source": "binance",
                    "full_symbol": symbol,
                    "24h_volume": quote_volume,
                })
                break
    
    symbol_candidates.sort(key=lambda x: x["24h_volume"], reverse=True)
    result = symbol_candidates[:SYMBOL_LIMIT]
    
    for item in result:
        item.pop("24h_volume", None)
        item.pop("full_symbol", None)
    
    logger.info(f"Filter 1 complete: Selected top {len(result)} active cryptocurrencies by 24h volume")
    return result


async def filter2(
    pool: asyncpg.Pool,
    symbols: List[Dict[str, str]]
) -> Dict[str, Tuple[date, date, Dict[str, str]]]:
    """
    Determine date ranges that need to be downloaded for each symbol.
    Checks existing data in database and identifies missing date ranges (up to 10 years).
    
    Args:
        pool: Database connection pool
        symbols: List of symbols from Filter 1
    
    Returns:
        Dictionary mapping symbol to (start_date, end_date, symbol_info)
    """
    # Import here to avoid circular import
    import sys
    import os
    filters_dir = os.path.dirname(os.path.abspath(__file__))
    crypto_etl_dir = os.path.dirname(filters_dir)
    if crypto_etl_dir in sys.path:
        sys.path.remove(crypto_etl_dir)
    sys.path.insert(0, crypto_etl_dir)
    from main import MAX_HISTORICAL_DAYS
    
    logger.info("Filter 2: Determining date ranges...")
    
    if not symbols:
        return {}
    
    today = datetime.now(timezone.utc).date()
    target_start = today - timedelta(days=MAX_HISTORICAL_DAYS)
    
    symbol_list = list(set(s["symbol"] for s in symbols))
    quote_list = list(set(s["quote_asset"] for s in symbols))
    symbol_quote_pairs = set((s["symbol"], s["quote_asset"]) for s in symbols)
    
    sql = """
        SELECT symbol, quote_asset, MIN(date) AS first_date, MAX(date) AS last_date
        FROM crypto_prices
        WHERE symbol = ANY($1::text[]) AND quote_asset = ANY($2::text[])
        GROUP BY symbol, quote_asset
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, symbol_list, quote_list)
    
    date_range_map = {}
    for row in rows:
        if (row["symbol"], row["quote_asset"]) in symbol_quote_pairs:
            first_date = row["first_date"]
            last_date = row["last_date"]
            
            # Convert to date object if needed
            if isinstance(first_date, str):
                first_date = datetime.strptime(first_date, "%Y-%m-%d").date()
            elif isinstance(first_date, datetime):
                first_date = first_date.date()
            elif not isinstance(first_date, date):
                first_date = date.fromisoformat(str(first_date)) if hasattr(date, 'fromisoformat') else datetime.strptime(str(first_date), "%Y-%m-%d").date()
            
            if isinstance(last_date, str):
                last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
            elif isinstance(last_date, datetime):
                last_date = last_date.date()
            elif not isinstance(last_date, date):
                last_date = date.fromisoformat(str(last_date)) if hasattr(date, 'fromisoformat') else datetime.strptime(str(last_date), "%Y-%m-%d").date()
            
            date_range_map[(row["symbol"], row["quote_asset"])] = (first_date, last_date)
    
    ranges = {}
    for sym_info in symbols:
        symbol = sym_info["symbol"]
        quote_asset = sym_info["quote_asset"]
        date_range = date_range_map.get((symbol, quote_asset))
        
        if date_range:
            first_date, last_date = date_range
            expected_start = today - timedelta(days=MAX_HISTORICAL_DAYS)
            
            needs_backfill = first_date > expected_start
            needs_forward_fill = last_date < today - timedelta(days=1)
            days_covered = (last_date - first_date).days + 1
            has_enough_days = days_covered >= MAX_HISTORICAL_DAYS
            
            if needs_backfill or not has_enough_days:
                start_date = target_start
            elif needs_forward_fill:
                start_date = last_date + timedelta(days=1)
            else:
                continue
        else:
            start_date = target_start
        
        if start_date > today:
            continue
        
        ranges[symbol] = (start_date, today, sym_info)
    
    logger.info(f"Filter 2 complete: Need to download data for {len(ranges)} symbols")
    return ranges


async def filter3(
    session: aiohttp.ClientSession,
    pool: asyncpg.Pool,
    ranges: Dict[str, Tuple[date, date, Dict[str, str]]]
) -> Dict[str, Dict[str, Any]]:
    """
    Download missing OHLCV data and store in database.

    Args:
        session: HTTP session for making API requests
        pool: Database connection pool
        ranges: Dictionary mapping symbol to (start_date, end_date, symbol_info) from Filter 2
    
    Returns:
        Dictionary mapping symbol to result info (rows_inserted, error)
    """
    # Import here to avoid circular import
    import sys
    import os
    filters_dir = os.path.dirname(os.path.abspath(__file__))
    crypto_etl_dir = os.path.dirname(filters_dir)
    if crypto_etl_dir in sys.path:
        sys.path.remove(crypto_etl_dir)
    sys.path.insert(0, crypto_etl_dir)
    from main import WORKERS, download_ohlcv, transform_binance_data
    from database import insert_price_data
    
    logger.info("Filter 3: Downloading and storing data...")
    
    semaphore = asyncio.Semaphore(WORKERS)
    results: Dict[str, Dict[str, Any]] = {}
    
    async def process_symbol(symbol: str, span: Tuple[date, date, Dict[str, str]]):
        async with semaphore:
            start_date, end_date, sym_info = span
            try:
                klines = await download_ohlcv(
                    session,
                    symbol,
                    sym_info["quote_asset"],
                    start_date,
                    end_date,
                )
                
                if not klines:
                    results[symbol] = {"rows": 0, "error": None}
                    return
                
                records = transform_binance_data(symbol, klines, sym_info["quote_asset"])
                inserted = await insert_price_data(pool, records)
                results[symbol] = {"rows": inserted, "error": None}
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                results[symbol] = {"rows": 0, "error": str(e)}
    
    tasks = [process_symbol(symbol, span) for symbol, span in ranges.items()]
    for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading", unit="symbol"):
        await coro
    
    logger.info(f"Filter 3 complete: Processed {len(results)} symbols")
    return results

