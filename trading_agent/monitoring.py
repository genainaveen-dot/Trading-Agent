from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any

from trading_agent.models import OrderPlan, PositionState, RiskDecision, SwingAlert, TradeSignal
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
    orders_file: Path = field(default_factory=lambda: Path("orders.json"))
    kill_switch: KillSwitch = field(default_factory=KillSwitch)
    signals: list[TradeSignal] = field(default_factory=list)
    positions: list[PositionState] = field(default_factory=list)
    orders: list[dict[str, Any]] = field(default_factory=list)
    alerts: list[SwingAlert] = field(default_factory=list)
    risk_decisions: list[RiskDecision] = field(default_factory=list)
    audit_log: list[dict[str, Any]] = field(default_factory=list)
    lock: Lock = field(default_factory=Lock)

    def __post_init__(self) -> None:
        self._load_orders()

    def _load_orders(self) -> None:
        if self.orders_file.exists():
            try:
                data = json.loads(self.orders_file.read_text(encoding="utf-8"))
                self.orders = data.get("orders", [])
                self.positions = [PositionState(**p) for p in data.get("positions", [])]
            except (json.JSONDecodeError, TypeError):
                self.orders = []
                self.positions = []

    def _save_orders(self) -> None:
        data = {
            "orders": self.orders[-1000:],
            "positions": [to_jsonable(p) for p in self.positions],
            "last_updated": datetime.now(UTC).isoformat(),
        }
        self.orders_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_signal(self, signal: TradeSignal) -> None:
        with self.lock:
            self.signals.append(signal)
            self._audit("signal", to_jsonable(signal))

    def add_order(self, order: OrderPlan, broker_response: dict[str, Any]) -> None:
        with self.lock:
            event = {"plan": to_jsonable(order), "broker_response": broker_response}
            self.orders.append(event)
            self._audit("order", event)
            self._save_orders()

    def add_position(self, position: PositionState) -> None:
        with self.lock:
            self.positions.append(position)
            self._save_orders()

    def update_position(self, symbol: str, status: str | None = None, realized_pnl: float | None = None) -> None:
        with self.lock:
            for pos in self.positions:
                if pos.symbol == symbol:
                    if status:
                        pos.status = status
                    if realized_pnl is not None:
                        pos.realized_pnl = realized_pnl
            self._save_orders()

    def add_alert(self, alert: SwingAlert) -> None:
        with self.lock:
            self.alerts.append(alert)
            self._audit("alert", to_jsonable(alert))

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
                "alerts": to_jsonable(self.alerts[-100:]),
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
