from __future__ import annotations

from trading_agent.models import CurveState, Zone


def analyze_curve(current_price: float, demand: Zone | None, supply: Zone | None) -> CurveState:
    if demand is None or supply is None:
        return CurveState.EQUILIBRIUM
    low = demand.proximal
    high = supply.proximal
    if high <= low:
        return CurveState.UNKNOWN
    position = (current_price - low) / (high - low)
    if position >= 0.875:
        return CurveState.VERY_HIGH
    if position >= 0.6667:
        return CurveState.HIGH
    if position <= 0.125:
        return CurveState.VERY_LOW
    if position <= 0.3333:
        return CurveState.LOW
    return CurveState.EQUILIBRIUM
