from __future__ import annotations

from pathlib import Path

from trading_agent.alerts import SwingAlertAgent
from trading_agent.config import AppConfig
from trading_agent.execution.base import ExecutionAdapter
from trading_agent.execution.dhan import DhanExecutionAdapter
from trading_agent.execution.kite import KiteExecutionAdapter
from trading_agent.execution.paper import PaperExecutionAdapter
from trading_agent.models import Candle, MarketSegment, PositionState, TIMEFRAME_PRESETS
from trading_agent.monitoring import AgentState
from trading_agent.notifications import create_notification_service
from trading_agent.risk import RiskManager
from trading_agent.strategy.engine import StrategyEngine


class TradingAgent:
    def __init__(
        self,
        config: AppConfig,
        execution: ExecutionAdapter | None = None,
        state: AgentState | None = None,
    ) -> None:
        self.config = config
        orders_file = Path("orders.json")
        self.state = state or AgentState(mode=config.mode, live_enabled=config.live_enabled, orders_file=orders_file)
        self.strategy = StrategyEngine(config.strategy)
        self.alerts = SwingAlertAgent()
        self.risk = RiskManager(config.risk)
        self.execution = execution or self._build_execution_adapter()
        self.notifications = create_notification_service()

    def process_symbol(
        self,
        symbol: str,
        htf_candles: list[Candle],
        itf_candles: list[Candle],
        ltf_candles: list[Candle],
        last_price: float | None = None,
        market_segment: MarketSegment = MarketSegment.EQUITY,
    ) -> None:
        preset = TIMEFRAME_PRESETS[self.config.timeframe_preset]
        allow_short = self.config.allow_swing_short
        signals = self.strategy.generate_signals(
            symbol=symbol,
            htf_candles=htf_candles,
            itf_candles=itf_candles,
            ltf_candles=ltf_candles,
            timeframe_preset=preset.name,
            allow_short=allow_short,
        )
        for signal in signals:
            self.state.add_signal(signal)
            if preset.name == "swing" and self.config.broker.name.lower() == "dhan":
                alert = self.alerts.build_alert(signal, market_segment)
                self.state.add_alert(alert)
                self.notifications.notify(alert.message)
            decision = self.risk.evaluate(
                signal,
                open_positions=self.state.positions,
                product=preset.product,
                last_price=last_price,
                live_enabled=self.config.mode == "paper" or self.config.live_enabled,
                kill_switch_enabled=self.state.kill_switch.enabled,
            )
            self.state.add_risk_decision(decision)
            if not decision.accepted or decision.order_plan is None:
                continue
            entry_response = self.execution.place_entry_order(decision.order_plan)
            self.state.add_order(decision.order_plan, entry_response)
            entry_order_id = str(entry_response.get("order_id", ""))
            exit_response = self.execution.place_exit_orders(decision.order_plan, entry_order_id)
            self.state.add_order(decision.order_plan, exit_response)
            position = PositionState(
                symbol=decision.order_plan.symbol,
                direction=decision.order_plan.direction,
                quantity=decision.order_plan.quantity,
                entry_price=decision.order_plan.entry,
                stop_loss=decision.order_plan.stop_loss,
                target=decision.order_plan.target,
                product=decision.order_plan.product,
                broker_order_ids=[
                    item
                    for item in [
                        entry_order_id,
                        str(exit_response.get("stop_order_id", "")),
                        str(exit_response.get("target_order_id", "")),
                        str(exit_response.get("gtt_trigger_id", "")),
                    ]
                    if item
                ],
            )
            self.state.add_position(position)

    def reconcile(self) -> dict[str, object]:
        return self.execution.reconcile()

    def _build_execution_adapter(self) -> ExecutionAdapter:
        if self.config.mode == "live":
            if not self.config.live_enabled:
                raise RuntimeError("mode is live but live_enabled is false")
            if self.config.broker.name.lower() == "dhan":
                return DhanExecutionAdapter(self.config.broker)
            if self.config.broker.name.lower() == "zerodha":
                return KiteExecutionAdapter(self.config.broker)
            raise RuntimeError(f"Unsupported broker: {self.config.broker.name}")
        return PaperExecutionAdapter()
