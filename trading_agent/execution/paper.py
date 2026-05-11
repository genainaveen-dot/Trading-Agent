from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from trading_agent.execution.base import ExecutionAdapter
from trading_agent.models import OrderPlan
from trading_agent.utils import to_jsonable


class PaperExecutionAdapter(ExecutionAdapter):
    def __init__(self) -> None:
        self.orders: list[dict[str, Any]] = []

    def place_entry_order(self, plan: OrderPlan) -> dict[str, Any]:
        order = {
            "order_id": f"paper-entry-{uuid4().hex[:12]}",
            "status": "COMPLETE",
            "filled_quantity": plan.quantity,
            "average_price": plan.entry,
            "created_at": datetime.now(UTC).isoformat(),
            "plan": to_jsonable(plan),
        }
        self.orders.append(order)
        return order

    def place_exit_orders(self, plan: OrderPlan, entry_order_id: str) -> dict[str, Any]:
        exits = {
            "parent_order_id": entry_order_id,
            "stop_order_id": f"paper-stop-{uuid4().hex[:12]}",
            "target_order_id": f"paper-target-{uuid4().hex[:12]}",
            "status": "OPEN",
            "stop_loss": plan.stop_loss,
            "target": plan.target,
            "created_at": datetime.now(UTC).isoformat(),
        }
        self.orders.append(exits)
        return exits

    def reconcile(self) -> dict[str, Any]:
        return {"orders": self.orders, "source": "paper"}
