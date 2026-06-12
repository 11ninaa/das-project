"""
Database connection pool management.
"""

import logging

import asyncpg

from .config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


async def create_db_pool() -> asyncpg.Pool:
    """Create database connection pool."""
    logger = logging.getLogger(__name__)
    logger.info(f"Connecting to PostgreSQL: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    try:
        pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            min_size=1,
            max_size=10,
        )

        async with pool.acquire() as conn:
            version = await conn.fetchval("SELECT version()")
            logger.info(f"Connected! PostgreSQL version: {version.split(',')[0]}")
        return pool
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.error("Make sure PostgreSQL is running and credentials are correct!")
        raise













