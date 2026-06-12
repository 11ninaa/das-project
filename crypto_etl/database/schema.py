"""
Database schema creation and migration.
"""

import logging

import asyncpg


async def apply_schema(pool: asyncpg.Pool):
    """Create database table if it doesn't exist and migrate if needed."""
    logger = logging.getLogger(__name__)
    
    async with pool.acquire() as conn:
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'crypto_prices'
            );
        """)
        
        if not table_exists:
            schema_sql = """
            CREATE TABLE crypto_prices (
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
            await conn.execute(schema_sql)
            logger.info("Database table created with new schema")
        else:
            constraint_name = await conn.fetchval("""
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_name = 'crypto_prices' 
                AND constraint_type = 'PRIMARY KEY';
            """)
            
            if constraint_name:
                pk_columns = await conn.fetch("""
                    SELECT column_name
                    FROM information_schema.key_column_usage
                    WHERE table_name = 'crypto_prices'
                    AND constraint_name = $1
                    ORDER BY ordinal_position;
                """, constraint_name)
                
                pk_cols = [row['column_name'] for row in pk_columns]

                if pk_cols == ['symbol', 'date']:
                    logger.info("Migrating table: changing primary key from (symbol, date) to (symbol, quote_asset, date)")

                    await conn.execute("""
                        ALTER TABLE crypto_prices 
                        ALTER COLUMN quote_asset SET NOT NULL;
                    """)

                    await conn.execute(f"""
                        ALTER TABLE crypto_prices 
                        DROP CONSTRAINT {constraint_name};
                    """)

                    await conn.execute("""
                        ALTER TABLE crypto_prices 
                        ADD PRIMARY KEY (symbol, quote_asset, date);
                    """)
                    
                    logger.info("Migration complete: primary key updated")
                elif pk_cols == ['symbol', 'quote_asset', 'date']:
                    logger.info("Table already has correct primary key")
                else:
                    logger.warning(f"Unexpected primary key columns: {pk_cols}")

            column_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'crypto_prices' 
                    AND column_name = 'number_of_trades'
                );
            """)
            
            if not column_exists:
                logger.info("Adding number_of_trades column for liquidity metrics")
                await conn.execute("""
                    ALTER TABLE crypto_prices 
                    ADD COLUMN number_of_trades INTEGER;
                """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_crypto_prices_date ON crypto_prices (date DESC);
                CREATE INDEX IF NOT EXISTS idx_crypto_prices_symbol ON crypto_prices (symbol);
                CREATE INDEX IF NOT EXISTS idx_crypto_prices_source ON crypto_prices (source);
            """)
    
    logger.info("Database schema ready")

























