from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from trading_agent.models import OrderPlan


class ExecutionAdapter(ABC):
    @abstractmethod
    def place_entry_order(self, plan: OrderPlan) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def place_exit_orders(self, plan: OrderPlan, entry_order_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def reconcile(self) -> dict[str, Any]:
        raise NotImplementedError
