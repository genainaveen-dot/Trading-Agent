from __future__ import annotations

from trading_agent.config import RiskConfig
from trading_agent.models import Direction, OrderPlan, PositionState, RiskDecision, TradeSignal
from trading_agent.utils import round_to_tick


class RiskManager:
    def __init__(self, config: RiskConfig | None = None) -> None:
        self.config = config or RiskConfig()
        self.daily_realized_pnl = 0.0

    @property
    def max_daily_loss_amount(self) -> float:
        return self.config.account_equity * (self.config.max_daily_loss_pct / 100)

    @property
    def risk_per_trade_amount(self) -> float:
        return self.config.account_equity * (self.config.risk_per_trade_pct / 100)

    def evaluate(
        self,
        signal: TradeSignal,
        open_positions: list[PositionState],
        product: str,
        last_price: float | None = None,
        live_enabled: bool = False,
        kill_switch_enabled: bool = False,
    ) -> RiskDecision:
        if kill_switch_enabled:
            return RiskDecision(False, "kill switch is enabled")
        if not live_enabled:
            return RiskDecision(False, "live execution is disabled; paper adapter may still simulate")
        if len([position for position in open_positions if position.status == "open"]) >= self.config.max_open_trades:
            return RiskDecision(False, "max open trades reached")
        if self.daily_realized_pnl <= -self.max_daily_loss_amount:
            return RiskDecision(False, "max daily loss reached")
        if product == "CNC" and signal.direction == Direction.SHORT:
            return RiskDecision(False, "cash-equity swing shorts are not allowed")
        if signal.score < 5:
            return RiskDecision(False, "trade score below 5")

        entry = round_to_tick(signal.entry, self.config.tick_size)
        stop = _buffered_stop(signal, self.config.stop_buffer_pct, self.config.tick_size)
        target = round_to_tick(signal.target, self.config.tick_size)
        risk_per_share = abs(entry - stop)
        if risk_per_share <= 0:
            return RiskDecision(False, "invalid entry/stop distance")

        if last_price is not None:
            slippage_pct = abs(entry - last_price) / last_price * 100 if last_price else 0
            if slippage_pct > self.config.max_slippage_pct:
                return RiskDecision(False, "entry slippage exceeds max_slippage_pct")

        quantity = int(self.risk_per_trade_amount // risk_per_share)
        if quantity <= 0:
            return RiskDecision(False, "risk budget too small for one share")

        plan = OrderPlan(
            symbol=signal.symbol,
            direction=signal.direction,
            quantity=quantity,
            entry=entry,
            stop_loss=stop,
            target=target,
            product=product,  # type: ignore[arg-type]
            metadata={
                "signal_score": signal.score,
                "entry_type": signal.entry_type.value,
                "pattern": signal.zone.pattern,
            },
        )
        return RiskDecision(
            True,
            "accepted",
            quantity=quantity,
            risk_amount=round(quantity * risk_per_share, 2),
            order_plan=plan,
        )

    def record_realized_pnl(self, pnl: float) -> None:
        self.daily_realized_pnl += pnl


def _buffered_stop(signal: TradeSignal, buffer_pct: float, tick_size: float) -> float:
    buffer_amount = signal.entry * (buffer_pct / 100)
    if signal.direction == Direction.LONG:
        return round_to_tick(signal.stop_loss - buffer_amount, tick_size)
    return round_to_tick(signal.stop_loss + buffer_amount, tick_size)
