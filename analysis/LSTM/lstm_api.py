"""
Standalone LSTM script for crypto price predictions, callable from a Java backend,
using pre-trained models or on-demand training with auto quote asset detection.
"""

import sys
import os
import json
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.data_fetcher import DataFetcher
from lstm_model import LSTMPredictor, LOOKBACK_WINDOW, TRAIN_SPLIT

PRE_TRAINED_SYMBOLS = [
    "BTC", "ETH", "BNB", "SOL", "ADA",
    "XRP", "DOGE", "DOT", "LTC", "AVAX"
]


try:
    from shared.utils import convert_to_native
except ImportError:
    def convert_to_native(obj):
        """Convert numpy/pandas types to native Python types for JSON."""
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
        else:
            return obj


async def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing symbol argument"}), file=sys.stderr)
        sys.exit(1)

    symbol = sys.argv[1].upper()
    days_ahead = int(sys.argv[2]) if len(sys.argv) > 2 else 7

    try:

        pool = await DataFetcher.create_connection_pool()
        fetcher = DataFetcher(pool)

        detected_quote = await fetcher.get_best_quote_asset(symbol)
        if not detected_quote:
            error = {
                "error": f"No data found for {symbol} in any quote asset (USDT, USDC, USD)"
            }
            print(json.dumps(error), file=sys.stderr)
            await pool.close()
            sys.exit(1)

        quote_asset = detected_quote

        df = await fetcher.fetch_all_available_data(symbol, quote_asset, auto_detect_quote=False)
        await pool.close()

        MIN_DATA_DAYS = 20
        
        if len(df) < MIN_DATA_DAYS:
            error = {
                "error": f"Insufficient data for {symbol}. Need at least {MIN_DATA_DAYS} days, got {len(df)}",
                "error_type": "insufficient_data",
                "required_days": MIN_DATA_DAYS,
                "available_days": len(df),
                "symbol": symbol,
                "quote_asset": quote_asset
            }
            print(json.dumps(error), file=sys.stderr)
            sys.exit(1)

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
                        from datetime import datetime
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

        future_prices = predictor.predict_future(scaled_data, days_ahead)

        last_price = float(df['close'].iloc[-1])

        result = {
            "symbol": symbol,
            "quote_asset": quote_asset,
            "last_price": last_price,
            "predicted_prices": [
                {"day": i + 1, "price": price}
                for i, price in enumerate(future_prices)
            ],
            "metrics": metrics,
            "training_info": training_info,
            "training_type": training_type,
            "is_pre_trained": is_pre_trained,
            "lookback_window": LOOKBACK_WINDOW,
            "train_split": TRAIN_SPLIT,
            "data_points": len(df),
            "last_trained_date": last_trained_date if last_trained_date else None
        }

        result = convert_to_native(result)

        print(json.dumps(result))

    except Exception as e:
        import traceback
        error_result = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())