from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from trading_agent.config import StrategyConfig
from trading_agent.models import (
    Candle,
    CurveState,
    Direction,
    TIMEFRAME_PRESETS,
    TradeSignal,
    TrendState,
    Zone,
    ZoneType,
)
from trading_agent.strategy.curve import analyze_curve
from trading_agent.strategy.scoring import entry_type_for_score, score_zone
from trading_agent.strategy.trend import analyze_trend
from trading_agent.strategy.zones import detect_zones, nearest_zones


class StrategyEngine:
    def __init__(self, config: StrategyConfig | None = None) -> None:
        self.config = config or StrategyConfig()

    def generate_signals(
        self,
        symbol: str,
        htf_candles: Sequence[Candle],
        itf_candles: Sequence[Candle],
        ltf_candles: Sequence[Candle],
        timeframe_preset: str,
    ) -> list[TradeSignal]:
        if not ltf_candles:
            return []
        preset = TIMEFRAME_PRESETS[timeframe_preset]
        current_price = ltf_candles[-1].close
        trend = analyze_trend(
            itf_candles,
            sma_period=self.config.sma_period,
            lookback=self.config.trend_lookback,
        )
        htf_demand, htf_supply = nearest_zones(htf_candles, current_price)
        curve = analyze_curve(current_price, htf_demand, htf_supply)
        zones = [
            score_zone(zone)
            for zone in detect_zones(ltf_candles, max_base_candles=self.config.max_base_candles)
        ]
        signals: list[TradeSignal] = []
        for zone in zones:
            signal = self._signal_from_zone(
                symbol=symbol,
                zone=zone,
                trend=trend,
                curve=curve,
                timeframe_preset=preset.name,
            )
            if signal is None:
                continue
            if signal.direction == Direction.SHORT and not preset.allow_short:
                continue
            signals.append(signal)
        return signals

    def _signal_from_zone(
        self,
        symbol: str,
        zone: Zone,
        trend: TrendState,
        curve: CurveState,
        timeframe_preset: str,
    ) -> TradeSignal | None:
        scored = score_zone(zone)
        entry_type = entry_type_for_score(scored.score)
        if entry_type is None:
            return None
        if scored.zone_type == ZoneType.DEMAND:
            if curve in {CurveState.HIGH, CurveState.VERY_HIGH}:
                return None
            if curve == CurveState.EQUILIBRIUM and trend != TrendState.UP:
                return None
            direction = Direction.LONG
            entry = scored.proximal
            stop = scored.distal
            risk = entry - stop
            if risk <= 0:
                return None
            target = entry + (self.config.target_r_multiple * risk)
        else:
            if curve in {CurveState.LOW, CurveState.VERY_LOW}:
                return None
            if curve == CurveState.EQUILIBRIUM and trend != TrendState.DOWN:
                return None
            direction = Direction.SHORT
            entry = scored.proximal
            stop = scored.distal
            risk = stop - entry
            if risk <= 0:
                return None
            target = entry - (self.config.target_r_multiple * risk)

        return TradeSignal(
            symbol=symbol,
            direction=direction,
            zone=replace(scored, score=scored.score),
            entry=entry,
            stop_loss=stop,
            target=target,
            score=scored.score,
            entry_type=entry_type,
            trend=trend,
            curve=curve,
            timeframe_preset=timeframe_preset,
            reason=f"{scored.pattern} {scored.zone_type.value} score={scored.score}",
        )
