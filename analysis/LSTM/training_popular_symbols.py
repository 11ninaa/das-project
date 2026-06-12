import sys
import os
import asyncio
import json
from datetime import datetime
import pandas as pd
from typing import Dict, Any, List


script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.data_fetcher import DataFetcher
from lstm_model import LSTMPredictor


class PopularSymbolsTrainer:
    POPULAR_SYMBOLS = [
        "BTC", "ETH", "BNB", "SOL", "ADA",
        "XRP", "DOGE", "DOT", "LTC", "AVAX"
    ]
    MIN_DATA_POINTS = 120
    LSTM_EPOCHS = 20

    def __init__(self, symbols: List[str] = POPULAR_SYMBOLS, epochs: int = LSTM_EPOCHS,
                 min_data: int = MIN_DATA_POINTS):
        """
        Initializes the LSTM model with given cryptocurrency symbols, training epochs, and minimum data requirement.
        """
        self.symbols = symbols
        self.epochs = epochs
        self.min_data = min_data
        self.start_time = None
        self.end_time = None

    async def _train_symbol_async(self, symbol: str) -> Dict[str, Any]:
        quote_asset = None
        pool = None

        print(f"[{symbol:<4}] Starting training...", end=" ", flush=True)

        try:
            pool = await DataFetcher.create_connection_pool()
            fetcher = DataFetcher(pool)

            detected_quote = await fetcher.get_best_quote_asset(symbol)
            if detected_quote:
                quote_asset = detected_quote
                print(f"(Asset: {quote_asset}) ", end="", flush=True)
            else:
                raise ValueError("No available Quote Asset.")

            df: pd.DataFrame = await fetcher.fetch_all_available_data(symbol, quote_asset, auto_detect_quote=False)

            if len(df) < self.min_data:
                raise ValueError(f"Insufficient data ({len(df)} < {self.min_data} days).")

            predictor = LSTMPredictor(epochs=self.epochs)
            X_train, y_train, X_val, y_val, _ = predictor.prepare_data(df)
            predictor.train(X_train, y_train, X_val, y_val)

            metrics = predictor.evaluate(X_val, y_val)
            predictor.save_model(symbol, quote_asset)

            print(f"Success. RMSE: {metrics['RMSE']:.2f}, MAPE: {metrics['MAPE']:.2f}%")

            return {
                "symbol": symbol,
                "quote_asset": quote_asset,
                "status": "success",
                "metrics": metrics,
                "data_points": len(df)
            }

        except Exception as e:
            error_msg = str(e)
            print(f"Error: {error_msg}")
            return {"symbol": symbol, "status": "failed", "error": error_msg}
        finally:
            if pool:
                await pool.close()

    async def run_batch_training(self):
        """
        Public function: Executes batch training in parallel for all symbols.
        Returns:
            List of training results for each symbol
        """
        print("\n" + "=" * 60)
        print(f"    LSTM {self.__class__.__name__} ")
        print("=" * 60)
        print(f"Starting training on {len(self.symbols)} cryptocurrencies.")
        print(f"Minimum data: {self.min_data} days | Epochs: {self.epochs}")
        print("------------------------------------------------------------")

        self.start_time = datetime.now()

        tasks = [self._train_symbol_async(symbol) for symbol in self.symbols]
        results: List[Dict[str, Any]] = await asyncio.gather(*tasks)

        self.end_time = datetime.now()
        self._print_summary(results)
        return results

    def _print_summary(self, results: List[Dict[str, Any]]):
        duration = (self.end_time - self.start_time).total_seconds()
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'failed']

        print("\n" + "=" * 70)
        print("Training Summary Report")
        print("=" * 70)
        print(f"Successfully trained: {len(successful)}/{len(self.symbols)}")
        print(f"Failed training: {len(failed)}/{len(self.symbols)}")
        print(f"Total time:      {duration / 60:.1f} minutes")
        print("-" * 70)

        if successful:
            print("\nSuccessfully Trained Models:")
            print(f"{'Symbol':<10} {'Asset':<8} {'RMSE':<12} {'MAPE':<10} {'R²':<10}")
            print("-" * 70)
            for r in successful:
                m = r['metrics']
                quote = r.get('quote_asset', 'N/A')
                print(f"{r['symbol']:<10} {quote:<8} {m['RMSE']:<12.2f} {m['MAPE']:<10.2f}% {m['R2']:<10.4f}")

        if failed:
            print("\nFailed Models:")
            for r in failed:
                print(f"-> {r['symbol']}: {r.get('error', 'Unknown error')}")

        results_file = os.path.join(os.path.dirname(__file__), "training_results.json")
        try:
            with open(results_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "duration_seconds": duration,
                    "total_symbols": len(self.symbols),
                    "successful_count": len(successful),
                    "results": results
                }, f, indent=2)
            print(f"\nResults saved to: {results_file}")
        except Exception as e:
            print(f"\nError saving JSON results: {e}")

        print("=" * 70)


if __name__ == "__main__":
    trainer = PopularSymbolsTrainer(epochs=30)
    asyncio.run(trainer.run_batch_training())