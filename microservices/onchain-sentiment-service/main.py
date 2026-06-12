"""
FastAPI microservice that combines on-chain metrics and sentiment analysis
 using the Strategy Pattern, exposing endpoints for analysis and health checks.
"""

import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import pathlib

current_dir = os.path.dirname(os.path.abspath(__file__))
# In Docker: main.py is at /app/main.py, analysis is at /app/analysis
analysis_dir = os.path.join(current_dir, "analysis")
if analysis_dir not in sys.path:
    sys.path.insert(0, analysis_dir)

onchain_dir = os.path.join(analysis_dir, "on_chain_and_sentiment_analysis")
if onchain_dir not in sys.path:
    sys.path.insert(0, onchain_dir)

from onchain_logic import OnChainLogic
from sentiment_logic import SentimentLogic
from strategies import WeightedAverageFusionStrategy
from shared.utils import convert_to_native

try:
    from dotenv import load_dotenv
    script_dir = pathlib.Path(__file__).parent
    analysis_path = pathlib.Path(analysis_dir)
    
    env_path = script_dir / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    original_env_path = analysis_path / 'on_chain_and_sentiment_analysis' / '.env'
    if original_env_path.exists():
        load_dotenv(original_env_path)
    else:
        load_dotenv()
except ImportError:
    pass

app = FastAPI(
    title="On-Chain & Sentiment Analysis Service",
    description="Microservice for cryptocurrency on-chain metrics and sentiment analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OnChainSentimentResponse(BaseModel):
    symbol: str
    decision: Dict[str, Any]
    onchain_details: Dict[str, Any]
    sentiment_details: Dict[str, Any]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "onchain-sentiment"}


@app.get("/api/onchain-sentiment/{symbol}", response_model=OnChainSentimentResponse)
async def get_onchain_sentiment(symbol: str):
    """
    Get combined on-chain and sentiment analysis for a cryptocurrency symbol,
    returning metrics, sentiment scores, and a final decision.
    """
    symbol = symbol.upper()
    
    try:
        try:
            from dotenv import load_dotenv
            script_dir = pathlib.Path(__file__).parent
            analysis_path = pathlib.Path(analysis_dir)
            
            env_path = script_dir / '.env'
            if env_path.exists():
                load_dotenv(env_path, override=False)
            else:
                original_env_path = analysis_path / 'on_chain_and_sentiment_analysis' / '.env'
                if original_env_path.exists():
                    load_dotenv(original_env_path, override=False)
        except ImportError:
            pass
        
        cryptopanic_key = os.getenv("CRYPTOPANIC_API_KEY")
        newsapi_key = os.getenv("NEWSAPI_KEY")
        
        onchain = OnChainLogic(symbol).analyze()
        
        sentiment = SentimentLogic(
            cryptopanic_api_key=cryptopanic_key,
            newsapi_key=newsapi_key
        ).analyze(symbol)
        
        fusion_strategy = WeightedAverageFusionStrategy(
            weights={"onchain": 0.75, "sentiment": 0.25}
        )
        signals = {
            "onchain": onchain["onchain_score"],
            "sentiment": sentiment["sentiment_score_norm"]
        }
        decision = fusion_strategy.fuse(signals)
        
        result = {
            "symbol": symbol,
            "decision": convert_to_native(decision),
            "onchain_details": convert_to_native(onchain),
            "sentiment_details": convert_to_native(sentiment)
        }
        
        return OnChainSentimentResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed for {symbol}: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

