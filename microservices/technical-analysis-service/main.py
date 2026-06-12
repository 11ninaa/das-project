"""
FastAPI microservice for cryptocurrency technical analysis,
providing indicators, oscillators, and trading signals via analysis and health endpoints.
"""

import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio

current_dir = os.path.dirname(os.path.abspath(__file__))
# In Docker: main.py is at /app/main.py, analysis is at /app/analysis
analysis_dir = os.path.join(current_dir, "analysis")
if analysis_dir not in sys.path:
    sys.path.insert(0, analysis_dir)

from shared.data_fetcher import DataFetcher
from shared.utils import convert_to_native

tech_analysis_dir = os.path.join(analysis_dir, "tech-analysis")
if tech_analysis_dir not in sys.path:
    sys.path.insert(0, tech_analysis_dir)
from signals import generate_signal

pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await DataFetcher.create_connection_pool()
    yield
    if pool:
        await pool.close()


app = FastAPI(
    title="Technical Analysis Service",
    description="Microservice for cryptocurrency technical analysis",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TechnicalAnalysisResponse(BaseModel):
    symbol: str
    timeframe: str
    signal: str
    confidence: float
    buy_votes: int
    sell_votes: int
    neutral_votes: int
    reasoning: str
    indicators: dict


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "technical-analysis"}


@app.get("/api/technical/{symbol}", response_model=TechnicalAnalysisResponse)
async def get_technical_analysis(
    symbol: str,
    timeframe: str = "1d"
):
    """
    Get technical analysis for a cryptocurrency symbol over a specified timeframe, returning indicators and trading signals.
    """
    symbol = symbol.upper()
    
    if timeframe not in ["1d", "1w", "1m"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid timeframe: {timeframe}. Must be one of: 1d, 1w, 1m"
        )
    
    if not pool:
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )
    
    try:
        fetcher = DataFetcher(pool)
        
        df_daily = await fetcher.fetch_all_available_data(symbol)
        
        if df_daily.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for symbol: {symbol}"
            )
        
        signal_result = generate_signal(df_daily, timeframe=timeframe)
        
        indicators_dict = convert_to_native(signal_result.indicators)
        
        result = {
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": signal_result.signal,
            "confidence": float(signal_result.confidence),
            "buy_votes": int(signal_result.buy_votes),
            "sell_votes": int(signal_result.sell_votes),
            "neutral_votes": int(signal_result.neutral_votes),
            "reasoning": signal_result.reasoning,
            "indicators": indicators_dict
        }
        
        return TechnicalAnalysisResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed for {symbol}: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

