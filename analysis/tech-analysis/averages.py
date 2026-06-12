import pandas as pd
import numpy as np
from ta.volatility import BollingerBands
from ta.trend import EMAIndicator

SMA_PERIOD = 20
EMA_PERIOD = 20
WMA_PERIOD = 20
BOLLINGER_PERIOD = 20
VOLUME_MA_PERIOD = 20

_TIMEFRAME_RULES = {
    "1d": "1D",
    "1w": "W",
    "1m": "ME",
}

class Averages:
    """
    Class to calculate Moving Averages and Bollinger Bands for OHLCV data.
    """

    def __init__(self, df: pd.DataFrame):

        self.df = df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df = self.df.sort_values('date').reset_index(drop=True)
        self.df = self.df.set_index('date')

    def resample(self, timeframe: str) -> pd.DataFrame:

        if timeframe not in _TIMEFRAME_RULES:
            raise ValueError(f"Invalid timeframe '{timeframe}'. Valid: {list(_TIMEFRAME_RULES.keys())}")

        rule = _TIMEFRAME_RULES[timeframe]
        df_resampled = self.df.resample(rule).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna(subset=['close'])

        return df_resampled

    def calculate_averages(
        self,
        sma_period: int = SMA_PERIOD,
        ema_period: int = EMA_PERIOD,
        wma_period: int = WMA_PERIOD,
        bollinger_period: int = BOLLINGER_PERIOD,
        volume_ma_period: int = VOLUME_MA_PERIOD,
        timeframe: str = "1d"
    ) -> pd.DataFrame:

        df_resampled = self.resample(timeframe)

        max_period = max(sma_period, ema_period, wma_period, bollinger_period, volume_ma_period)
        if len(df_resampled) < max_period:
            raise ValueError(
                f"Not enough resampled periods for the requested indicators/periods. "
                f"Rows={len(df_resampled)}, needed={max_period}"
            )

        # SMA
        df_resampled['sma'] = df_resampled['close'].rolling(window=sma_period).mean()

        # EMA
        ema_indicator = EMAIndicator(close=df_resampled['close'], window=ema_period)
        df_resampled['ema'] = ema_indicator.ema_indicator()

        # WMA
        weights = np.arange(1, wma_period + 1)
        df_resampled['wma'] = df_resampled['close'].rolling(window=wma_period).apply(
            lambda x: np.sum(x * weights) / np.sum(weights), raw=True
        )

        # Bollinger Bands
        bb = BollingerBands(close=df_resampled['close'], window=bollinger_period, window_dev=2)
        df_resampled['bb_mband'] = bb.bollinger_mavg()
        df_resampled['bb_hband'] = bb.bollinger_hband()
        df_resampled['bb_lband'] = bb.bollinger_lband()

        # Volume Moving Average
        df_resampled['vol_ma'] = df_resampled['volume'].rolling(window=volume_ma_period).mean()

        # Reset index to have 'date' as a column
        return df_resampled.reset_index()
