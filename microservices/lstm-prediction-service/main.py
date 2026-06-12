"""
FastAPI microservice for LSTM-based cryptocurrency
price prediction using pre-trained models or on-demand training, exposed via a single prediction endpoint.
"""
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
# In Docker: main.py is at /app/main.py, analysis is at /app/analysis
analysis_dir = os.path.join(current_dir, "analysis")
if analysis_dir not in sys.path:
    sys.path.insert(0, analysis_dir)

from shared.data_fetcher import DataFetcher
from shared.utils import convert_to_native

lstm_dir = os.path.join(analysis_dir, "LSTM")
if lstm_dir not in sys.path:
    sys.path.insert(0, lstm_dir)
from lstm_model import LSTMPredictor, LOOKBACK_WINDOW, TRAIN_SPLIT

PRE_TRAINED_SYMBOLS = [
    "BTC", "ETH", "BNB", "SOL", "ADA",
    "XRP", "DOGE", "DOT", "LTC", "AVAX"
]

pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global pool
    pool = await DataFetcher.create_connection_pool()
    yield
    if pool:
        await pool.close()


app = FastAPI(
    title="LSTM Prediction Service",
    description="Microservice for cryptocurrency price predictions using LSTM",
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


class PredictedPrice(BaseModel):
    day: int
    price: float


class LSTMPredictionResponse(BaseModel):
    symbol: str
    quote_asset: str
    last_price: float
    predicted_prices: List[PredictedPrice]
    metrics: dict
    training_info: str
    training_type: str
    is_pre_trained: bool
    lookback_window: int
    train_split: float
    data_points: int
    last_trained_date: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "lstm-prediction"}


@app.get("/api/lstm/{symbol}", response_model=LSTMPredictionResponse)
async def get_lstm_prediction(
    symbol: str,
    daysAhead: int = 7
):
    """
    Get LSTM-based price predictions for a given cryptocurrency symbol over a
    specified number of future days, returning predicted prices and model metrics.
    """
    symbol = symbol.upper()
    
    if daysAhead < 1 or daysAhead > 30:
        raise HTTPException(
            status_code=400,
            detail="daysAhead must be between 1 and 30"
        )
    
    if not pool:
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )
    
    try:
        fetcher = DataFetcher(pool)
        
        detected_quote = await fetcher.get_best_quote_asset(symbol)
        if not detected_quote:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {symbol} in any quote asset (USDT, USDC, USD)"
            )
        
        quote_asset = detected_quote
        
        df = await fetcher.fetch_all_available_data(symbol, quote_asset, auto_detect_quote=False)
        
        MIN_DATA_DAYS = 20
        if len(df) < MIN_DATA_DAYS:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for {symbol}. Need at least {MIN_DATA_DAYS} days, got {len(df)}"
            )
        
        model_exists = LSTMPredictor.model_exists(symbol, quote_asset)
        last_trained_date = LSTMPredictor.get_last_trained_date(symbol, quote_asset)
        latest_db_date = str(df['date'].max())
        
        is_pre_trained = symbol.upper() in PRE_TRAINED_SYMBOLS
        
        training_info = ""
        training_type = ""
        predictor = None
        needs_training = False
        
        if not model_exists:
            training_type = "on-demand"
            training_info = "On-demand Training"
            needs_training = True
            predictor = LSTMPredictor(epochs=10)
        else:
            try:
                predictor = LSTMPredictor.load_model(symbol, quote_asset)
                
                if is_pre_trained:
                    training_type = "pre-trained"
                    training_info = "Pre-trained Model (Cached)"
                    needs_training = False
                else:
                    if last_trained_date:
                        try:
                            trained_date = datetime.fromisoformat(last_trained_date.replace('Z', '+00:00')).date()
                            latest_date = pd.to_datetime(df['date'].max()).date()
                            
                            if latest_date > trained_date:
                                days_diff = (latest_date - trained_date).days
                                if days_diff > 1:
                                    training_type = "on-demand"
                                    training_info = "Fine-tuned (data updated)"
                                    needs_training = True
                                    predictor.epochs = 5
                                else:
                                    training_type = "on-demand"
                                    training_info = "Previously Trained (Cached)"
                                    needs_training = False
                            else:
                                training_type = "on-demand"
                                training_info = "Previously Trained (Cached)"
                                needs_training = False
                        except Exception:
                            training_type = "on-demand"
                            training_info = "Previously Trained (Cached)"
                            needs_training = False
                    else:
                        training_type = "on-demand"
                        training_info = "Previously Trained (Cached)"
                        needs_training = False
            except Exception as e:
                training_type = "pre-trained" if is_pre_trained else "on-demand"
                training_info = "Retrained (model incompatible)"
                needs_training = True
                predictor = LSTMPredictor(epochs=10)
        
        X_train, y_train, X_val, y_val, scaled_data = predictor.prepare_data(df)
        
        if needs_training:
            predictor.train(X_train, y_train, X_val, y_val)
            predictor.save_model(symbol, quote_asset)
        
        metrics = predictor.evaluate(X_val, y_val)
        
        future_prices = predictor.predict_future(scaled_data, daysAhead)
        
        last_price = float(df['close'].iloc[-1])
        
        result = {
            "symbol": symbol,
            "quote_asset": quote_asset,
            "last_price": last_price,
            "predicted_prices": [
                {"day": i + 1, "price": float(price)}
                for i, price in enumerate(future_prices)
            ],
            "metrics": convert_to_native(metrics),
            "training_info": training_info,
            "training_type": training_type,
            "is_pre_trained": is_pre_trained,
            "lookback_window": LOOKBACK_WINDOW,
            "train_split": TRAIN_SPLIT,
            "data_points": len(df),
            "last_trained_date": last_trained_date if last_trained_date else None
        }
        
        return LSTMPredictionResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed for {symbol}: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

