from __future__ import annotations

from collections.abc import Sequence

from trading_agent.models import Candle, TrendState


def analyze_trend(
    candles: Sequence[Candle],
    sma_period: int = 50,
    lookback: int = 7,
    flat_tolerance_pct: float = 0.05,
) -> TrendState:
    if len(candles) < sma_period + lookback:
        return TrendState.SIDEWAYS
    closes = [candle.close for candle in candles]
    current_sma = _sma(closes[-sma_period:])
    previous_sma = _sma(closes[-sma_period - lookback : -lookback])
    if previous_sma == 0:
        return TrendState.SIDEWAYS
    slope_pct = ((current_sma - previous_sma) / previous_sma) * 100
    if abs(slope_pct) <= flat_tolerance_pct:
        return TrendState.SIDEWAYS
    return TrendState.UP if slope_pct > 0 else TrendState.DOWN


def _sma(values: Sequence[float]) -> float:
    return sum(values) / len(values)
