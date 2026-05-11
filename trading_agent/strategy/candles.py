from __future__ import annotations

from trading_agent.models import Candle, CandleKind


def classify_candle(candle: Candle) -> CandleKind:
    if candle.range <= 0:
        return CandleKind.NEUTRAL
    body_ratio = candle.body / candle.range
    if body_ratio > 0.5:
        return CandleKind.EXCITING
    if body_ratio < 0.5:
        return CandleKind.BASE
    return CandleKind.NEUTRAL


def is_rally(candle: Candle) -> bool:
    return classify_candle(candle) == CandleKind.EXCITING and candle.is_bullish


def is_drop(candle: Candle) -> bool:
    return classify_candle(candle) == CandleKind.EXCITING and candle.is_bearish
