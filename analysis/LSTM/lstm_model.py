"""
LSTM model for cryptocurrency price prediction using TensorFlow/Keras
 with 70/30 train/validation split and evaluation via MSE, RMSE, MAPE, and R².
"""

import os
import json
import numpy as np
import pandas as pd
import pickle
from datetime import datetime
from typing import Dict, Tuple, Optional

from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout
from keras.callbacks import EarlyStopping, ModelCheckpoint

# Scikit-learn
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, r2_score

LOOKBACK_WINDOW = 60
TRAIN_SPLIT = 0.70
LSTM_UNITS = 50
DROPOUT_RATE = 0.2
EPOCHS = 20
BATCH_SIZE = 32

_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(_MODEL_DIR, exist_ok=True)


def calculate_mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100


def create_sequences(data: np.ndarray, lookback: int) -> Tuple[np.ndarray, np.ndarray]:
    X, y = [], []
    for i in range(lookback, len(data)):
        X.append(data[i - lookback:i])
        y.append(data[i, 0])
    return np.array(X), np.array(y)


class LSTMPredictor:

    def __init__(self, lookback: int = None, epochs: int = EPOCHS):
        self.lookback = lookback
        self.epochs = epochs
        self.model = None
        self.scaler_features = MinMaxScaler(feature_range=(0, 1))
        self.scaler_target = MinMaxScaler(feature_range=(0, 1))

    def _calculate_adaptive_lookback(self, data_length: int) -> int:
        """
        Calculate adaptive lookback window based on available data.
        Ensures we have enough data for training while maximizing lookback.
        """

        if data_length < 20:
            return max(3, data_length // 3)
        elif data_length < 60:
            return max(7, data_length // 3)
        elif data_length < 120:
            return max(14, min(30, data_length // 4))
        else:
            return LOOKBACK_WINDOW

    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for LSTM training.
        Uses OHLCV features (5 features) + close target (1 feature) = 6 features total.
        """
        df = df.sort_values('date').reset_index(drop=True)

        if self.lookback is None:
            self.lookback = self._calculate_adaptive_lookback(len(df))

        features = df[['open', 'high', 'low', 'close', 'volume']].values.astype('float32')
        target = df[['close']].values.astype('float32')


        split_idx = int(len(features) * TRAIN_SPLIT)

        self.scaler_features.fit(features[:split_idx])
        self.scaler_target.fit(target[:split_idx])

        features_scaled = self.scaler_features.transform(features)
        target_scaled = self.scaler_target.transform(target)

        combined = np.hstack([features_scaled, target_scaled])

        X, y = create_sequences(combined, self.lookback)

        if len(X) < 5:
            raise ValueError(
                f"Insufficient data for {len(df)} days. "
                f"After creating sequences with lookback={self.lookback}, only {len(X)} samples available. "
                f"Need at least 5 samples for training."
            )

        train_size = max(1, int(len(X) * TRAIN_SPLIT))
        if train_size < 3:
            X_train, X_val = X, X[-1:] if len(X) > 1 else X
            y_train, y_val = y, y[-1:] if len(y) > 1 else y
        else:
            X_train, X_val = X[:train_size], X[train_size:]
            y_train, y_val = y[:train_size], y[train_size:]

        return X_train, y_train, X_val, y_val, combined

    def build_model(self, input_shape: Tuple[int, int]):
        """Build LSTM model architecture."""

        if self.lookback <= 14:
            lstm_units = 25
        elif self.lookback <= 30:
            lstm_units = 35
        else:
            lstm_units = LSTM_UNITS

        self.model = Sequential([
            LSTM(lstm_units, return_sequences=True, input_shape=input_shape),
            Dropout(DROPOUT_RATE),
            LSTM(lstm_units, return_sequences=False),
            Dropout(DROPOUT_RATE),
            Dense(1)
        ])
        self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray, y_val: np.ndarray) -> Dict:
        """Train the model."""
        if self.model is None:
            self.build_model((X_train.shape[1], X_train.shape[2]))

        batch_size = BATCH_SIZE
        if len(X_train) < batch_size:
            batch_size = max(1, len(X_train) // 2)  # Use smaller batch size

        epochs = self.epochs
        if len(X_train) < 20:
            epochs = min(epochs * 2, 30)  # More epochs for very small datasets

        callbacks = [
            EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
            ModelCheckpoint(
                os.path.join(_MODEL_DIR, 'temp_best_model.h5'),
                monitor='val_loss',
                save_best_only=True,
                verbose=0
            )
        ]

        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=0
        )

        return history.history

    def evaluate(self, X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, float]:
        """Evaluate model and return metrics."""
        y_pred_scaled = self.model.predict(X_val, verbose=0)
        y_pred = self.scaler_target.inverse_transform(y_pred_scaled.reshape(-1, 1))
        y_actual = self.scaler_target.inverse_transform(y_val.reshape(-1, 1))

        rmse = np.sqrt(mean_squared_error(y_actual, y_pred))
        mape = calculate_mape(y_actual, y_pred)
        r2 = r2_score(y_actual, y_pred)

        return {
            'RMSE': float(rmse),
            'MAPE': float(mape),
            'R2': float(r2)
        }

    def predict_future(self, scaled_data: np.ndarray, days_ahead: int = 7) -> list:
        """
        Predict next N days.
        scaled_data should have 6 features [OHLCV (5) + close target (1)]
        """
        predictions = []
        last_sequence = scaled_data[-self.lookback:].reshape(1,self.lookback, scaled_data.shape[1])

        for _ in range(days_ahead):
            next_pred_scaled= self.model.predict(last_sequence, verbose=0)
            predictions.append(next_pred_scaled[0,0])

            new_row = np.zeros((1, 1, scaled_data.shape[1]) )
            last_row = last_sequence[0, -1, :].copy()

            new_row[0, 0, 0:5] = last_row[0:5]

            new_row[0, 0, 3] = next_pred_scaled[0, 0]

            new_row[0, 0, 5] = next_pred_scaled[0, 0]

            if new_row[0, 0, 1] < new_row[0, 0, 3]:
                new_row[0, 0, 1] = new_row[0, 0, 3]
            if new_row[0, 0, 2] > new_row[0, 0, 3]:
                new_row[0, 0, 2] = new_row[0, 0, 3]

            last_sequence = np.concatenate([last_sequence[:, 1:, :], new_row], axis=1)

        predictions = np.array(predictions).reshape(-1, 1)
        future_prices = self.scaler_target.inverse_transform(predictions)

        return future_prices.flatten().tolist()

    def save_model(self, symbol: str, quote_asset: str = "USDT"):
        """Save model and scalers."""
        model_path = os.path.join(_MODEL_DIR, f"{symbol}_{quote_asset}_model.h5")
        scaler_X_path =os.path.join(_MODEL_DIR, f"{symbol}_{quote_asset}_scaler_X.pkl")
        scaler_Y_path =os.path.join(_MODEL_DIR, f"{symbol}_{quote_asset}_scaler_Y.pkl")
        meta_path = os.path.join(_MODEL_DIR, f"{symbol}_{quote_asset}_meta.json")
        self.model.save(model_path)

        with open(scaler_X_path, 'wb') as f:
            pickle.dump(self.scaler_features, f)
        with open(scaler_Y_path, 'wb') as f:
            pickle.dump(self.scaler_target, f)

        meta = {
            "symbol": symbol,
            "quote_asset": quote_asset,
            "last_trained_date": datetime.now().isoformat(),
            "lookback": self.lookback,
            "epochs": self.epochs
        }
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)

    @staticmethod
    def load_model(symbol: str, quote_asset: str = "USDT") -> 'LSTMPredictor':
        """Load pre-trained model."""
        model_path = os.path.join(_MODEL_DIR, f"{symbol}_{quote_asset}_model.h5")
        scaler_X_path = os.path.join(_MODEL_DIR, f"{symbol}_{quote_asset}_scaler_X.pkl")
        scaler_Y_path = os.path.join(_MODEL_DIR, f"{symbol}_{quote_asset}_scaler_Y.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")

        predictor = LSTMPredictor()

        try:
            predictor.model = load_model(model_path, compile=False)
            predictor.model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        except Exception as e:
            try:
                predictor.model = load_model(model_path)
            except Exception as e2:
                raise RuntimeError(f"Failed to load model: {str(e)}. Secondary error: {str(e2)}")

        with open(scaler_X_path, 'rb') as f:
            predictor.scaler_features = pickle.load(f)
        with open(scaler_Y_path, 'rb') as f:
            predictor.scaler_target = pickle.load(f)

        return predictor

    @staticmethod
    def model_exists(symbol: str, quote_asset: str = "USDT") -> bool:
        model_path = os.path.join(_MODEL_DIR, f"{symbol}_{quote_asset}_model.h5")
        return os.path.exists(model_path)

    @staticmethod
    def get_last_trained_date(symbol: str, quote_asset: str = "USDT") -> Optional[str]:
        meta_path = os.path.join(_MODEL_DIR, f"{symbol}_{quote_asset}_meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
                return meta.get("last_trained_date")
        return None