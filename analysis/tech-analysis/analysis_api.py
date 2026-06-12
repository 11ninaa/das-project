
import sys
import json
import asyncio
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.data_fetcher import DataFetcher
from signals import generate_signal


async def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing symbol argument"}), file=sys.stderr)
        sys.exit(1)

    symbol = sys.argv[1].upper()
    timeframe = sys.argv[2] if len(sys.argv) > 2 else "1d"

    if timeframe not in ["1d", "1w", "1m"]:
        print(json.dumps({"error": f"Invalid timeframe: {timeframe}"}), file=sys.stderr)
        sys.exit(1)

    try:
        pool = await DataFetcher.create_connection_pool()
        fetcher = DataFetcher(pool)

        df_daily = await fetcher.fetch_all_available_data(symbol)

        signal_result = generate_signal(df_daily, timeframe=timeframe)

        try:
            from shared.utils import convert_to_native
        except ImportError:
            def convert_to_native(obj):
                """Recursively convert numpy/pandas types to native Python types."""
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
            "indicators": indicators_dict  # Use the detailed indicators structure directly
        }

        print(json.dumps(result))

        await pool.close()

    except Exception as e:
        error_result = {"error": str(e)}
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
