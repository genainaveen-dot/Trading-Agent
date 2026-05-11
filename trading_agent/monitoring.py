from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any

from trading_agent.models import OrderPlan, PositionState, RiskDecision, TradeSignal
from trading_agent.utils import to_jsonable


@dataclass
class KillSwitch:
    enabled: bool = False
    reason: str = ""
    updated_at: datetime | None = None

    def set(self, enabled: bool, reason: str = "") -> None:
        self.enabled = enabled
        self.reason = reason
        self.updated_at = datetime.now(UTC)


@dataclass
class AgentState:
    mode: str
    live_enabled: bool
    kill_switch: KillSwitch = field(default_factory=KillSwitch)
    signals: list[TradeSignal] = field(default_factory=list)
    positions: list[PositionState] = field(default_factory=list)
    orders: list[dict[str, Any]] = field(default_factory=list)
    risk_decisions: list[RiskDecision] = field(default_factory=list)
    audit_log: list[dict[str, Any]] = field(default_factory=list)
    lock: Lock = field(default_factory=Lock)

    def add_signal(self, signal: TradeSignal) -> None:
        with self.lock:
            self.signals.append(signal)
            self._audit("signal", to_jsonable(signal))

    def add_order(self, order: OrderPlan, broker_response: dict[str, Any]) -> None:
        with self.lock:
            event = {"plan": to_jsonable(order), "broker_response": broker_response}
            self.orders.append(event)
            self._audit("order", event)

    def add_risk_decision(self, decision: RiskDecision) -> None:
        with self.lock:
            self.risk_decisions.append(decision)
            self._audit("risk", to_jsonable(decision))

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            return {
                "mode": self.mode,
                "live_enabled": self.live_enabled,
                "kill_switch": to_jsonable(self.kill_switch),
                "signals": to_jsonable(self.signals[-100:]),
                "positions": to_jsonable(self.positions),
                "orders": to_jsonable(self.orders[-100:]),
                "risk_decisions": to_jsonable(self.risk_decisions[-100:]),
                "audit_log": to_jsonable(self.audit_log[-100:]),
            }

    def _audit(self, event_type: str, payload: Any) -> None:
        self.audit_log.append(
            {
                    "timestamp": datetime.now(UTC).isoformat(),
                "event_type": event_type,
                "payload": payload,
            }
        )
