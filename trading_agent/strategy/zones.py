from __future__ import annotations

from collections.abc import Sequence

from trading_agent.models import Candle, Zone, ZoneType
from trading_agent.strategy.candles import classify_candle
from trading_agent.models import CandleKind


def detect_zones(candles: Sequence[Candle], max_base_candles: int = 6) -> list[Zone]:
    zones: list[Zone] = []
    if len(candles) < 3:
        return zones

    for legin_idx in range(0, len(candles) - 2):
        legin = candles[legin_idx]
        if classify_candle(legin) != CandleKind.EXCITING:
            continue
        for base_count in range(1, max_base_candles + 1):
            base_start_idx = legin_idx + 1
            base_end_idx = legin_idx + base_count
            legout_idx = base_end_idx + 1
            if legout_idx >= len(candles):
                break
            bases = candles[base_start_idx : base_end_idx + 1]
            if not all(classify_candle(candle) == CandleKind.BASE for candle in bases):
                break
            legout = candles[legout_idx]
            if classify_candle(legout) != CandleKind.EXCITING:
                continue
            zone_type = ZoneType.DEMAND if legout.is_bullish else ZoneType.SUPPLY
            pattern = _pattern_name(legin, legout)
            proximal, distal = _zone_lines(zone_type, bases)
            tested_count = _count_zone_tests(candles[legout_idx + 1 :], proximal, distal)
            zones.append(
                Zone(
                    symbol=legout.symbol,
                    zone_type=zone_type,
                    pattern=pattern,
                    proximal=proximal,
                    distal=distal,
                    base_start=bases[0].timestamp,
                    base_end=bases[-1].timestamp,
                    legin_time=legin.timestamp,
                    legout_time=legout.timestamp,
                    base_count=base_count,
                    tested_count=tested_count,
                    legout_strength=_legout_strength(candles, legout_idx),
                    has_gap=_has_legout_gap(zone_type, bases[-1], legout),
                    fresh=tested_count == 0,
                )
            )
    return _dedupe_zones(zones)


def nearest_zones(candles: Sequence[Candle], current_price: float) -> tuple[Zone | None, Zone | None]:
    zones = detect_zones(candles)
    fresh = [zone for zone in zones if zone.fresh]
    demand = [
        zone
        for zone in fresh
        if zone.zone_type == ZoneType.DEMAND and zone.proximal <= current_price
    ]
    supply = [
        zone
        for zone in fresh
        if zone.zone_type == ZoneType.SUPPLY and zone.proximal >= current_price
    ]
    nearest_demand = max(demand, key=lambda zone: zone.proximal, default=None)
    nearest_supply = min(supply, key=lambda zone: zone.proximal, default=None)
    return nearest_demand, nearest_supply


def _pattern_name(legin: Candle, legout: Candle) -> str:
    left = "R" if legin.is_bullish else "D"
    right = "R" if legout.is_bullish else "D"
    return f"{left}B{right}"


def _zone_lines(zone_type: ZoneType, bases: Sequence[Candle]) -> tuple[float, float]:
    if zone_type == ZoneType.DEMAND:
        proximal = max(candle.upper_body for candle in bases)
        distal = min(candle.low for candle in bases)
    else:
        proximal = min(candle.lower_body for candle in bases)
        distal = max(candle.high for candle in bases)
    return proximal, distal


def _count_zone_tests(candles: Sequence[Candle], proximal: float, distal: float) -> int:
    top = max(proximal, distal)
    bottom = min(proximal, distal)
    touches = 0
    for candle in candles:
        if candle.low <= top and candle.high >= bottom:
            touches += 1
    return touches


def _has_legout_gap(zone_type: ZoneType, last_base: Candle, legout: Candle) -> bool:
    if zone_type == ZoneType.DEMAND:
        return legout.open > last_base.high
    return legout.open < last_base.low


def _legout_strength(candles: Sequence[Candle], legout_idx: int) -> str:
    legout = candles[legout_idx]
    ratio = legout.body / legout.range if legout.range else 0
    next_same_exciting = False
    if legout_idx + 1 < len(candles):
        next_candle = candles[legout_idx + 1]
        next_same_exciting = (
            classify_candle(next_candle) == CandleKind.EXCITING
            and next_candle.is_bullish == legout.is_bullish
        )
    if ratio >= 0.75 or next_same_exciting:
        return "very_strong"
    if ratio >= 0.6:
        return "strong"
    return "normal"


def _dedupe_zones(zones: list[Zone]) -> list[Zone]:
    seen: set[tuple[str, ZoneType, str, float, float]] = set()
    unique: list[Zone] = []
    for zone in zones:
        key = (
            zone.symbol,
            zone.zone_type,
            zone.legout_time.isoformat(),
            round(zone.proximal, 4),
            round(zone.distal, 4),
        )
        if key not in seen:
            seen.add(key)
            unique.append(zone)
    return unique
