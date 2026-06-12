"""
API module combining on-chain and sentiment analysis using the Strategy Pattern,
 callable from a Java backend and returning JSON results.
"""

import sys
import json
import os
from typing import Dict, Any

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from onchain_logic import OnChainLogic
from sentiment_logic import SentimentLogic
from strategies import WeightedAverageFusionStrategy

try:
    from shared.utils import convert_to_native
except ImportError:
    def convert_to_native(obj):
        """Convert numpy/pandas types to native Python types for JSON serialization."""
        import numpy as np
        import pandas as pd
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, (np.ndarray, pd.Series)):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_to_native(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return convert_to_native(obj.__dict__)
        else:
            return obj


try:
    from dotenv import load_dotenv
    import pathlib

    script_dir = pathlib.Path(__file__).parent
    env_path = script_dir / '.env'

    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
except ImportError:

    pass



def analyze(symbol: str) -> Dict[str, Any]:
    """
    Performs complete analysis for a given symbol.
    """
    try:
        try:
            from dotenv import load_dotenv
            import pathlib
            script_dir = pathlib.Path(__file__).parent
            env_path = script_dir / '.env'
            if env_path.exists():
                load_dotenv(env_path, override=False)  # Don't override if already set
        except ImportError:
            pass
        
        # Get API keys from environment
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
            "symbol": symbol.upper(),
            "decision": decision,
            "onchain_details": onchain,
            "sentiment_details": sentiment
        }

        return convert_to_native(result)

    except Exception as e:
        import traceback
        error_details = f"Analysis failed for {symbol}: {str(e)}\nTraceback: {traceback.format_exc()}"
        raise Exception(error_details)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing symbol argument"}), file=sys.stderr)
        sys.exit(1)

    symbol = sys.argv[1].upper()

    try:
        result = analyze(symbol)
        print(json.dumps(result))
    except Exception as e:
        error_result = {"error": str(e)}
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

from fastapi import FastAPI
app = FastAPI(title="On-Chain & Sentiment Analysis API")

@app.get("/analyze/{symbol}")
def analyze_endpoint(symbol: str) -> Dict[str, Any]:
    """HTTP endpoint for analysis."""
    return analyze(symbol)