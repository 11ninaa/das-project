import pandas as pd
from typing import Literal, Dict, Any
from dataclasses import dataclass

from oscillators import (
    calculate_rsi, calculate_macd, calculate_stochastic,
    calculate_adx, calculate_cci,
    RSI_OVERSOLD, RSI_OVERBOUGHT,
    STOCH_OVERSOLD, STOCH_OVERBOUGHT,
    CCI_OVERBOUGHT, CCI_OVERSOLD,
    ADX_STRONG_TREND, ADX_WEAK_TREND
)
from averages import Averages


@dataclass
class SignalResult:
    signal: str
    confidence: float
    buy_votes: int
    sell_votes: int
    neutral_votes: int
    reasoning: str
    indicators: Dict[str, Any]


def generate_signal(df: pd.DataFrame, timeframe: Literal["1d", "1w", "1m"] = "1d") -> SignalResult:
    """
    Generate BUY/SELL/HOLD signal by analyzing all 10 indicators.
    """

    buy_votes = 0
    sell_votes = 0
    neutral_votes = 0
    reasoning_parts = []
    indicator_details = {}

    # OSCILLATOR 1: RSI
    try:
        rsi_df = calculate_rsi(df, timeframe=timeframe)
        rsi_value = rsi_df['rsi'].iloc[-1]
        if rsi_value < RSI_OVERSOLD:
            buy_votes += 1
            rsi_signal = "BUY"
            reasoning_parts.append(f"RSI oversold ({rsi_value:.2f}) - potential buying opportunity")
        elif rsi_value > RSI_OVERBOUGHT:
            sell_votes += 1
            rsi_signal = "SELL"
            reasoning_parts.append(f"RSI overbought ({rsi_value:.2f}) - potential selling opportunity")
        else:
            neutral_votes += 1
            rsi_signal = "NEUTRAL"

        indicator_details['rsi'] = {'value': rsi_value, 'signal': rsi_signal}
    except Exception as e:
        neutral_votes += 1
        indicator_details['rsi'] = {'value': None, 'signal': 'NEUTRAL', 'error': str(e)}


    # OSCILLATOR 2: MACD
    try:
        macd_df = calculate_macd(df, timeframe=timeframe)
        macd_line = macd_df['macd'].iloc[-1]
        signal_line = macd_df['macd_signal'].iloc[-1]
        histogram = macd_df['macd_histogram'].iloc[-1]

        if histogram > 0 and macd_line > signal_line:
            buy_votes += 1
            macd_signal = "BUY"
            reasoning_parts.append("MACD bullish (above signal, histogram positive)")
        elif histogram < 0 and macd_line < signal_line:
            sell_votes += 1
            macd_signal = "SELL"
            reasoning_parts.append("MACD bearish (below signal, histogram negative)")
        else:
            neutral_votes += 1
            macd_signal = "NEUTRAL"

        indicator_details['macd'] = {
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram,
            'signal': macd_signal
        }
    except Exception as e:
        neutral_votes += 1
        indicator_details['macd'] = {'value': None, 'signal': 'NEUTRAL', 'error': str(e)}

    # OSCILLATOR 3: Stochastic
    try:
        stoch_df = calculate_stochastic(df, timeframe=timeframe)
        k_value = stoch_df['stoch_k'].iloc[-1]
        d_value = stoch_df['stoch_d'].iloc[-1]

        if k_value < STOCH_OVERSOLD:  # < 20
            buy_votes += 1
            stoch_signal = "BUY"
            reasoning_parts.append(f"Stochastic oversold (%K={k_value:.2f})")
        elif k_value > STOCH_OVERBOUGHT:
            sell_votes += 1
            stoch_signal = "SELL"
            reasoning_parts.append(f"Stochastic overbought (%K={k_value:.2f})")
        elif k_value > d_value:
            buy_votes += 1
            stoch_signal = "BUY"
            reasoning_parts.append("Stochastic %K crossing above %D (bullish)")
        else:
            neutral_votes += 1
            stoch_signal = "NEUTRAL"

        indicator_details['stochastic'] = {
            'k': k_value,
            'd': d_value,
            'signal': stoch_signal
        }
    except Exception as e:
        neutral_votes += 1
        indicator_details['stochastic'] = {'value': None, 'signal': 'NEUTRAL', 'error': str(e)}

    # OSCILLATOR 4: ADX (measures trend strength)
    try:
        adx_df = calculate_adx(df, timeframe=timeframe)
        adx_value = adx_df['adx'].iloc[-1]


        if adx_value > ADX_STRONG_TREND:
            adx_signal = "STRONG_TREND"
        elif adx_value < ADX_WEAK_TREND:
            adx_signal = "WEAK_TREND"
            neutral_votes += 1
        else:
            adx_signal = "MODERATE_TREND"

        indicator_details['adx'] = {'value': adx_value, 'signal': adx_signal}
    except Exception as e:
        neutral_votes += 1
        indicator_details['adx'] = {'value': None, 'signal': 'NEUTRAL', 'error': str(e)}

    # OSCILLATOR 5: CCI
    try:
        cci_df = calculate_cci(df, timeframe=timeframe)
        cci_value = cci_df['cci'].iloc[-1]

        if cci_value < CCI_OVERSOLD:
            buy_votes += 1
            cci_signal = "BUY"
            reasoning_parts.append(f"CCI oversold ({cci_value:.2f})")
        elif cci_value > CCI_OVERBOUGHT:
            sell_votes += 1
            cci_signal = "SELL"
            reasoning_parts.append(f"CCI overbought ({cci_value:.2f})")
        else:
            neutral_votes += 1
            cci_signal = "NEUTRAL"

        indicator_details['cci'] = {'value': cci_value, 'signal': cci_signal}
    except Exception as e:
        neutral_votes += 1
        indicator_details['cci'] = {'value': None, 'signal': 'NEUTRAL', 'error': str(e)}


    # MOVING AVERAGE 1: SMA (Simple Moving Average)
    try:
        averages = Averages(df)
        avg_df = averages.calculate_averages(timeframe=timeframe)
        latest = avg_df.iloc[-1]

        current_price = latest['close']
        sma_value = latest['sma']

        if pd.notna(sma_value):
            price_vs_sma_percent = ((current_price - sma_value) / sma_value) * 100

            if price_vs_sma_percent > 2:
                buy_votes += 1
                sma_signal = "BUY"
                reasoning_parts.append(f"Price {price_vs_sma_percent:.1f}% above SMA (bullish)")
            elif price_vs_sma_percent < -2:
                sell_votes += 1
                sma_signal = "SELL"
                reasoning_parts.append(f"Price {price_vs_sma_percent:.1f}% below SMA (bearish)")
            else:
                neutral_votes += 1
                sma_signal = "NEUTRAL"
        else:
            sma_signal = "NEUTRAL"
            neutral_votes += 1

        indicator_details['sma'] = {
            'value': sma_value,
            'price_vs_sma_percent': price_vs_sma_percent if pd.notna(sma_value) else None,
            'signal': sma_signal
        }
    except Exception as e:
        neutral_votes += 1
        indicator_details['sma'] = {'value': None, 'signal': 'NEUTRAL', 'error': str(e)}

    # MOVING AVERAGE 2: EMA (Exponential Moving Average)
    try:
        ema_value = latest['ema']
        if pd.notna(ema_value):
            price_vs_ema_percent = ((current_price - ema_value) / ema_value) * 100

            if price_vs_ema_percent > 2:
                buy_votes += 1
                ema_signal = "BUY"
                reasoning_parts.append(f"Price {price_vs_ema_percent:.1f}% above EMA")
            elif price_vs_ema_percent < -2:
                sell_votes += 1
                ema_signal = "SELL"
                reasoning_parts.append(f"Price {price_vs_ema_percent:.1f}% below EMA")
            else:
                neutral_votes += 1
                ema_signal = "NEUTRAL"
        else:
            ema_signal = "NEUTRAL"
            neutral_votes += 1

        indicator_details['ema'] = {
            'value': ema_value,
            'price_vs_ema_percent': price_vs_ema_percent if pd.notna(ema_value) else None,
            'signal': ema_signal
        }
    except Exception as e:
        neutral_votes += 1
        indicator_details['ema'] = {'value': None, 'signal': 'NEUTRAL', 'error': str(e)}

    # MOVING AVERAGE 3: WMA (Weighted Moving Average)
    try:
        wma_value = latest['wma']
        if pd.notna(wma_value):
            price_vs_wma_percent = ((current_price - wma_value) / wma_value) * 100

            if price_vs_wma_percent > 2:
                buy_votes += 1
                wma_signal = "BUY"
            elif price_vs_wma_percent < -2:
                sell_votes += 1
                wma_signal = "SELL"
            else:
                neutral_votes += 1
                wma_signal = "NEUTRAL"
        else:
            wma_signal = "NEUTRAL"
            neutral_votes += 1

        indicator_details['wma'] = {
            'value': wma_value,
            'price_vs_wma_percent': price_vs_wma_percent if pd.notna(wma_value) else None,
            'signal': wma_signal
        }
    except Exception as e:
        neutral_votes += 1
        indicator_details['wma'] = {'value': None, 'signal': 'NEUTRAL', 'error': str(e)}

    # MOVING AVERAGE 4: Bollinger Bands
    try:
        bb_upper = latest['bb_hband']
        bb_middle = latest['bb_mband']
        bb_lower = latest['bb_lband']

        if pd.notna(bb_upper) and pd.notna(bb_lower):
            if current_price < bb_lower:
                buy_votes += 1
                bb_signal = "BUY"
                reasoning_parts.append("Price below lower Bollinger Band (oversold)")
            elif current_price > bb_upper:
                sell_votes += 1
                bb_signal = "SELL"
                reasoning_parts.append("Price above upper Bollinger Band (overbought)")
            elif current_price > bb_middle:
                buy_votes += 1
                bb_signal = "BUY"
            else:
                neutral_votes += 1
                bb_signal = "NEUTRAL"
        else:
            bb_signal = "NEUTRAL"
            neutral_votes += 1

        indicator_details['bollinger_bands'] = {
            'upper': bb_upper,
            'middle': bb_middle,
            'lower': bb_lower,
            'signal': bb_signal
        }
    except Exception as e:
        neutral_votes += 1
        indicator_details['bollinger_bands'] = {'value': None, 'signal': 'NEUTRAL', 'error': str(e)}

    # MOVING AVERAGE 5: Volume MA
    try:
        volume_ma = latest['vol_ma']
        current_volume = latest['volume']

        if pd.notna(volume_ma) and pd.notna(current_volume):
            volume_ratio = current_volume / volume_ma
            if volume_ratio > 1.2:
                vol_signal = "HIGH_VOLUME"
            elif volume_ratio < 0.8:
                vol_signal = "LOW_VOLUME"
            else:
                vol_signal = "NORMAL_VOLUME"
        else:
            vol_signal = "NORMAL_VOLUME"

        indicator_details['volume_ma'] = {
            'value': volume_ma,
            'current_volume': current_volume,
            'volume_ratio': volume_ratio if pd.notna(volume_ma) else None,
            'signal': vol_signal
        }
    except Exception as e:
        indicator_details['volume_ma'] = {'value': None, 'signal': 'NORMAL_VOLUME', 'error': str(e)}

    # DETERMINE FINAL SIGNAL (Majority Vote)

    total_votes = buy_votes + sell_votes + neutral_votes

    if total_votes == 0:
        return SignalResult(
            signal="HOLD",
            confidence=0.0,
            buy_votes=0,
            sell_votes=0,
            neutral_votes=0,
            reasoning="No indicators available",
            indicators=indicator_details
        )

    if buy_votes > sell_votes:
        signal = "BUY"
        confidence = buy_votes / total_votes
    elif sell_votes > buy_votes:
        signal = "SELL"
        confidence = sell_votes / total_votes
    else:
        signal = "HOLD"
        confidence = 0.5

    if indicator_details.get('adx', {}).get('signal') == "STRONG_TREND":
        confidence = min(1.0, confidence * 1.2)

    if indicator_details.get('volume_ma', {}).get('signal') == "HIGH_VOLUME":
        confidence = min(1.0, confidence * 1.1)
    elif indicator_details.get('volume_ma', {}).get('signal') == "LOW_VOLUME":
        confidence = max(0.0, confidence * 0.9)

    if reasoning_parts:
        reasoning = f"{signal} signal: " + "; ".join(reasoning_parts[:5])
    else:
        reasoning = f"{signal} signal: Mixed or neutral indicators"

    return SignalResult(
        signal=signal,
        confidence=round(confidence, 3),
        buy_votes=buy_votes,
        sell_votes=sell_votes,
        neutral_votes=neutral_votes,
        reasoning=reasoning,
        indicators=indicator_details
    )
