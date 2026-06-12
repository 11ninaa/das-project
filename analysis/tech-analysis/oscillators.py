import pandas as pd
import logging
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD,ADXIndicator,CCIIndicator
from typing import Literal, Optional

logger = logging.getLogger(__name__)

RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9

STOCH_PERIOD = 14
STOCH_SMOOTH_K = 3
STOCH_SMOOTH_D = 3
STOCH_OVERSOLD = 20
STOCH_OVERBOUGHT = 80

ADX_PERIOD = 14
ADX_STRONG_TREND = 25
ADX_WEAK_TREND = 20

CCI_PERIOD = 20
CCI_OVERBOUGHT = 100
CCI_OVERSOLD = -100

_TIMEFRAME_RULES = {
    "1d": "1D",
    "1w": "W",
    "1m": "ME",
}


def calculate_rsi(
        df: pd.DataFrame,
        period: int = RSI_PERIOD,
        timeframe: Literal["1D", "1W", "1M"] = "1d",
        drop: bool = True
) -> pd.DataFrame:
    """
    Calculate RSI for the given timeframe.
    """
    if "close" not in df.columns:
        raise ValueError("DataFrame must contain 'close' column.")
    if "date" not in df.columns:
        raise ValueError("DataFrame must contain 'date' column.")

    if timeframe not in _TIMEFRAME_RULES:
        raise ValueError(f"Invalid timeframe '{timeframe}'. Valid: {list(_TIMEFRAME_RULES.keys())}")

    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"])
    df_copy = df_copy.sort_values("date").reset_index(drop=True)
    df_copy = df_copy.set_index("date")

    resample_rule = _TIMEFRAME_RULES[timeframe]

    df_resampled = df_copy.resample(resample_rule).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    })

    df_resampled = df_resampled.dropna(subset=["close"])

    if len(df_resampled) < period + 1:
        raise ValueError(
            f"Not enough data after resampling for RSI(period={period}) on timeframe {timeframe}. "
            f"Rows={len(df_resampled)}, needed={period + 1}"
        )

    rsi_indicator = RSIIndicator(close=df_resampled["close"], window=period)
    df_resampled = df_resampled.assign(rsi=rsi_indicator.rsi())

    if drop:
        df_resampled = df_resampled.dropna(subset=["rsi"])

    df_out = df_resampled.reset_index()

    return df_out


def calculate_macd(
        df: pd.DataFrame,
        fast_period: int = MACD_FAST_PERIOD,
        slow_period: int = MACD_SLOW_PERIOD,
        signal_period: int = MACD_SIGNAL_PERIOD,
        timeframe: Literal["1d", "1w", "1m"] = "1d",
        drop: bool = True
) -> pd.DataFrame:
    """
    Calculate MACD (Moving Average Convergence Divergence) for the given timeframe.

    MACD consists of three components:
    - MACD line: Difference between fast EMA (12) and slow EMA (26)
    - Signal line: EMA of MACD line (9 period)
    - Histogram: Difference between MACD line and Signal line

    """
    if "close" not in df.columns:
        raise ValueError("DataFrame must contain 'close' column.")
    if "date" not in df.columns:
        raise ValueError("DataFrame must contain 'date' column.")

    if timeframe not in _TIMEFRAME_RULES:
        raise ValueError(f"Invalid timeframe '{timeframe}'. Valid: {list(_TIMEFRAME_RULES.keys())}")

    if fast_period >= slow_period:
        raise ValueError(f"fast_period ({fast_period}) must be less than slow_period ({slow_period})")
    if fast_period < 1 or slow_period < 1 or signal_period < 1:
        raise ValueError("All periods must be positive integers")

    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"])
    df_copy = df_copy.sort_values("date").reset_index(drop=True)
    df_copy = df_copy.set_index("date")

    resample_rule = _TIMEFRAME_RULES[timeframe]

    df_resampled = df_copy.resample(resample_rule).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    })

    df_resampled = df_resampled.dropna(subset=["close"])

    min_required = slow_period + signal_period + 5  # Extra buffer for stability
    if len(df_resampled) < min_required:
        raise ValueError(
            f"Not enough data after resampling for MACD(fast={fast_period}, slow={slow_period}, "
            f"signal={signal_period}) on timeframe {timeframe}. "
            f"Rows={len(df_resampled)}, needed={min_required}"
        )

    macd_indicator = MACD(
        close=df_resampled["close"],
        window_fast=fast_period,
        window_slow=slow_period,
        window_sign=signal_period
    )

    df_resampled = df_resampled.assign(
        macd=macd_indicator.macd(),
        macd_signal=macd_indicator.macd_signal(),
        macd_histogram=macd_indicator.macd_diff()  # Histogram = MACD - Signal
    )

    if drop:
        df_resampled = df_resampled.dropna(subset=["macd", "macd_signal", "macd_histogram"])

    df_out = df_resampled.reset_index()

    return df_out

def calculate_stochastic(
        df: pd.DataFrame,
        period: int = STOCH_PERIOD,
        smooth_k: int = STOCH_SMOOTH_K,
        smooth_d: int = STOCH_SMOOTH_D,
        timeframe: Literal["1d", "1w", "1m"] = "1d",
        drop: bool = True
) -> pd.DataFrame:
    """
    Stochastic Oscillator compares the closing price to the price range over a period.
    It consists of two lines:
    - %K (fast): Raw stochastic value
    - %D (slow): Smoothed %K line

    Range: 0-100
    - >80 = overbought (sell signal)
    - <20 = oversold (buy signal)

    """
    required_columns = ['high', 'low', 'close', 'date']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"DataFrame must contain columns: {missing_columns}")

    if timeframe not in _TIMEFRAME_RULES:
        raise ValueError(f"Invalid timeframe '{timeframe}'. Valid: {list(_TIMEFRAME_RULES.keys())}")

    if period < 1:
        raise ValueError(f"period must be positive, got {period}")
    if smooth_k < 1:
        raise ValueError(f"smooth_k must be positive, got {smooth_k}")
    if smooth_d < 1:
        raise ValueError(f"smooth_d must be positive, got {smooth_d}")

    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"])
    df_copy = df_copy.sort_values("date").reset_index(drop=True)
    df_copy = df_copy.set_index("date")

    resample_rule = _TIMEFRAME_RULES[timeframe]

    df_resampled = df_copy.resample(resample_rule).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    })

    df_resampled = df_resampled.dropna(subset=["high", "low", "close"])

    min_required = period + smooth_k + smooth_d + 5  # Extra buffer for stability
    if len(df_resampled) < min_required:
        raise ValueError(
            f"Not enough data after resampling for Stochastic(period={period}, "
            f"smooth_k={smooth_k}, smooth_d={smooth_d}) on timeframe {timeframe}. "
            f"Rows={len(df_resampled)}, needed={min_required}"
        )

    stoch_indicator = StochasticOscillator(
        high=df_resampled["high"],
        low=df_resampled["low"],
        close=df_resampled["close"],
        window=period,
        smooth_window=smooth_k,
        fillna=False
    )

    df_resampled = df_resampled.assign(
        stoch_k=stoch_indicator.stoch(),
        stoch_d=stoch_indicator.stoch_signal()
    )

    if drop:
        df_resampled = df_resampled.dropna(subset=["stoch_k", "stoch_d"])

    df_out = df_resampled.reset_index()

    return df_out

def calculate_adx(
        df: pd.DataFrame,
        period: int = ADX_PERIOD,
        timeframe: Literal["1d", "1w", "1m"] = "1d",
        drop: bool = True
) -> pd.DataFrame:
    """
    Calculate ADX (Average Directional Index) for the given timeframe.

    ADX measures trend strength (not direction). It indicates how strong
    a trend is, regardless of whether it's up or down.

    """
    required_columns = ['high', 'low', 'close', 'date']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"DataFrame must contain columns: {missing_columns}")

    if timeframe not in _TIMEFRAME_RULES:
        raise ValueError(f"Invalid timeframe '{timeframe}'. Valid: {list(_TIMEFRAME_RULES.keys())}")

    if period < 1:
        raise ValueError(f"period must be positive, got {period}")

    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"])
    df_copy = df_copy.sort_values("date").reset_index(drop=True)
    df_copy = df_copy.set_index("date")

    resample_rule = _TIMEFRAME_RULES[timeframe]

    df_resampled = df_copy.resample(resample_rule).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    })

    df_resampled = df_resampled.dropna(subset=["high", "low", "close"])

    min_required = period * 2 + 5
    if len(df_resampled) < min_required:
        raise ValueError(
            f"Not enough data after resampling for ADX(period={period}) on timeframe {timeframe}. "
            f"Rows={len(df_resampled)}, needed={min_required}"
        )

    adx_indicator = ADXIndicator(
        high=df_resampled["high"],
        low=df_resampled["low"],
        close=df_resampled["close"],
        window=period,
        fillna=False
    )

    df_resampled = df_resampled.assign(
        adx=adx_indicator.adx()
    )

    if drop:
        df_resampled = df_resampled.dropna(subset=["adx"])

    df_out = df_resampled.reset_index()

    return df_out

def calculate_cci(
        df: pd.DataFrame,
        period: int = CCI_PERIOD,
        timeframe: Literal["1d", "1w", "1m"] = "1d",
        drop: bool = True
) -> pd.DataFrame:
    """
    Calculate CCI (Commodity Channel Index) for the given timeframe.

    CCI identifies cyclical trends by comparing current price to average price.
    It can move above +100 and below -100, unlike RSI/Stochastic which are bounded.
    """
    required_columns = ['high', 'low', 'close', 'date']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"DataFrame must contain columns: {missing_columns}")

    if timeframe not in _TIMEFRAME_RULES:
        raise ValueError(f"Invalid timeframe '{timeframe}'. Valid: {list(_TIMEFRAME_RULES.keys())}")

    if period < 1:
        raise ValueError(f"period must be positive, got {period}")

    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"])
    df_copy = df_copy.sort_values("date").reset_index(drop=True)
    df_copy = df_copy.set_index("date")

    resample_rule = _TIMEFRAME_RULES[timeframe]

    df_resampled = df_copy.resample(resample_rule).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    })

    df_resampled = df_resampled.dropna(subset=["high", "low", "close"])

    min_required = period + 5
    if len(df_resampled) < min_required:
        raise ValueError(
            f"Not enough data after resampling for CCI(period={period}) on timeframe {timeframe}. "
            f"Rows={len(df_resampled)}, needed={min_required}"
        )

    cci_indicator = CCIIndicator(
        high=df_resampled["high"],
        low=df_resampled["low"],
        close=df_resampled["close"],
        window=period,
        constant=0.015,
        fillna=False
    )

    df_resampled = df_resampled.assign(
        cci=cci_indicator.cci()
    )

    if drop:
        df_resampled = df_resampled.dropna(subset=["cci"])

    df_out = df_resampled.reset_index()

    return df_out
