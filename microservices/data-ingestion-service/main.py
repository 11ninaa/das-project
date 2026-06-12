import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import aiohttp

current_dir = os.path.dirname(os.path.abspath(__file__))

# In Docker: main.py is at /app/main.py, crypto_etl is at /app/crypto_etl
etl_path = os.path.join(current_dir, "crypto_etl")

if etl_path in sys.path:
    sys.path.remove(etl_path)
sys.path.insert(0, etl_path)

from filters import filter1, filter2, filter3

from database.connection import create_db_pool

db_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global db_pool
    db_pool = await create_db_pool()
    yield
    if db_pool:
        await db_pool.close()


app = FastAPI(
    title="Data Ingestion Microservice",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "data-ingestion"}


@app.get("/api/data/update")
async def trigger_etl(background_tasks: BackgroundTasks):
    """
    Endpoint triggered by the Java backend to start the ETL pipeline.
    """
    background_tasks.add_task(run_pipeline)
    return {
        "status": "started",
        "message": "ETL filters are running in the background."
    }


async def run_pipeline():
    """
    Executes the ETL pipeline by running the filters sequentially.
    """
    async with aiohttp.ClientSession() as session:
        try:
            # Execute filters in the predefined order
            symbols = await filter1(session)
            ranges = await filter2(db_pool, symbols)
            await filter3(session, db_pool, ranges)

            print("ETL process completed successfully.")
        except Exception as e:
            print(f"Error while executing ETL pipeline: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
