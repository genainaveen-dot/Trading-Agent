from __future__ import annotations

from trading_agent.models import MarketSegment, SwingAlert, TradeSignal


class SwingAlertAgent:
    """Turns strategy signals into Dhan swing-trading alerts."""

    def build_alert(self, signal: TradeSignal, market_segment: MarketSegment) -> SwingAlert:
        side = signal.direction.value.upper()
        segment = market_segment.value.upper()
        message = (
            f"{segment} swing {side} alert for {signal.symbol}: "
            f"entry {signal.entry:.2f}, SL {signal.stop_loss:.2f}, "
            f"target {signal.target:.2f}, score {signal.score:.1f}, "
            f"pattern {signal.zone.pattern}."
        )
        return SwingAlert(
            symbol=signal.symbol,
            market_segment=market_segment,
            direction=signal.direction,
            entry=signal.entry,
            stop_loss=signal.stop_loss,
            target=signal.target,
            score=signal.score,
            pattern=signal.zone.pattern,
            trend=signal.trend,
            curve=signal.curve,
            message=message,
        )
