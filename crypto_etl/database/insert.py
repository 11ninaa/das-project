"""
Database data insertion operations.
"""

import logging
from datetime import date
from typing import TYPE_CHECKING, List

import asyncpg

if TYPE_CHECKING:
    import sys
    import os
    insert_dir = os.path.dirname(os.path.abspath(__file__))
    crypto_etl_dir = os.path.dirname(insert_dir)
    if crypto_etl_dir not in sys.path:
        sys.path.insert(0, crypto_etl_dir)
    from main import PriceRecord


async def insert_price_data(pool: asyncpg.Pool, records: List['PriceRecord']) -> int:
    """
    Insert price data into database in batches.
    Args:
        pool: Database connection pool
        records: List of PriceRecord objects to insert
    Returns:
        Number of records processed (inserted or updated)
    """
    # Import here to avoid circular import at runtime
    import sys
    import os
    insert_dir = os.path.dirname(os.path.abspath(__file__))
    crypto_etl_dir = os.path.dirname(insert_dir)
    if crypto_etl_dir in sys.path:
        sys.path.remove(crypto_etl_dir)
    sys.path.insert(0, crypto_etl_dir)
    from main import PriceRecord

    logger = logging.getLogger(__name__)

    if not records:
        return 0

    BATCH_SIZE = 10000
    total_processed = 0

    async with pool.acquire() as conn:
        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i:i + BATCH_SIZE]

            try:
                async with conn.transaction():
                    batch_data = []
                    for record in batch:
                        date_value = record.date
                        if hasattr(date_value, 'date'):
                            date_value = date_value.date()
                        if not isinstance(date_value, date):
                            if isinstance(date_value, str):
                                from datetime import datetime
                                date_value = datetime.strptime(date_value, "%Y-%m-%d").date()
                            else:
                                raise ValueError(f"Invalid date type: {type(date_value)}")

                        batch_data.append((
                            record.symbol.upper(),
                            record.base_asset,
                            record.quote_asset,
                            record.source,
                            date_value,
                            record.open,
                            record.high,
                            record.low,
                            record.close,
                            record.volume,
                            record.quote_volume,
                            record.number_of_trades,
                        ))
                    await conn.executemany(
                        """
                        INSERT INTO crypto_prices (
                            symbol, base_asset, quote_asset, source, date,
                            open, high, low, close, volume, quote_volume, number_of_trades, updated_at
                        ) VALUES ($1, $2, $3, $4, $5::DATE, $6, $7, $8, $9, $10, $11, $12, NOW())
                        ON CONFLICT (symbol, quote_asset, date) DO UPDATE
                        SET base_asset = EXCLUDED.base_asset,
                            quote_asset = EXCLUDED.quote_asset,
                            source = EXCLUDED.source,
                            open = EXCLUDED.open,
                            high = EXCLUDED.high,
                            low = EXCLUDED.low,
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume,
                            quote_volume = EXCLUDED.quote_volume,
                            number_of_trades = EXCLUDED.number_of_trades,
                            updated_at = NOW();
                        """,
                        batch_data
                    )
                    total_processed += len(batch_data)
            except Exception as e:
                logger.error(f"Error inserting batch {i // BATCH_SIZE + 1}: {e}", exc_info=True)
                raise

    return total_processed
