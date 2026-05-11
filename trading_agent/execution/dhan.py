from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from trading_agent.config import BrokerConfig
from trading_agent.execution.base import ExecutionAdapter
from trading_agent.instruments import Instrument, load_dhan_instruments
from trading_agent.models import Direction, OrderPlan


class DhanExecutionAdapter(ExecutionAdapter):
    """DhanHQ live execution adapter.

    Dhan orders require a broker `security_id`, so this adapter reads a CSV map
    keyed by trading symbol before placing any live order.
    """

    def __init__(
        self,
        config: BrokerConfig,
        *,
        client: Any | None = None,
        instruments: dict[str, Instrument] | None = None,
    ) -> None:
        self.client_id = os.environ.get(config.client_id_env)
        self.access_token = os.environ.get(config.access_token_env)
        if not self.client_id or not self.access_token:
            raise RuntimeError(
                f"Dhan credentials are missing. Set {config.client_id_env} and "
                f"{config.access_token_env} in .env or PowerShell."
            )
        self.instruments = instruments or load_dhan_instruments(config.instrument_map_path)
        self.dhan = client or self._build_client()

    def place_entry_order(self, plan: OrderPlan) -> dict[str, Any]:
        instrument = self._instrument(plan.symbol)
        response = self.dhan.place_order(
            security_id=instrument.security_id,
            exchange_segment=instrument.exchange_segment,
            transaction_type=_transaction_type(plan.direction),
            quantity=plan.quantity,
            order_type="LIMIT",
            product_type=_product_type(plan.product),
            price=plan.entry,
            validity="DAY",
            correlation_id=_correlation_id("entry"),
        )
        return _normalize_order_response(response)

    def place_exit_orders(self, plan: OrderPlan, entry_order_id: str) -> dict[str, Any]:
        instrument = self._instrument(plan.symbol)
        exit_side = Direction.SHORT if plan.direction == Direction.LONG else Direction.LONG
        stop_response = self.dhan.place_order(
            security_id=instrument.security_id,
            exchange_segment=instrument.exchange_segment,
            transaction_type=_transaction_type(exit_side),
            quantity=plan.quantity,
            order_type="STOP_LOSS",
            product_type=_product_type(plan.product),
            price=plan.stop_loss,
            trigger_price=plan.stop_loss,
            validity="DAY",
            correlation_id=_correlation_id("stop"),
        )
        target_response = self.dhan.place_order(
            security_id=instrument.security_id,
            exchange_segment=instrument.exchange_segment,
            transaction_type=_transaction_type(exit_side),
            quantity=plan.quantity,
            order_type="LIMIT",
            product_type=_product_type(plan.product),
            price=plan.target,
            validity="DAY",
            correlation_id=_correlation_id("target"),
        )
        stop = _normalize_order_response(stop_response)
        target = _normalize_order_response(target_response)
        return {
            "parent_order_id": entry_order_id,
            "stop_order_id": stop.get("order_id", ""),
            "target_order_id": target.get("order_id", ""),
            "status": "OPEN",
            "oco_mode": "manual",
            "broker": "dhan",
            "raw": {"stop": stop_response, "target": target_response},
        }

    def reconcile(self) -> dict[str, Any]:
        return {
            "orders": self.dhan.get_order_list(),
            "positions": self.dhan.get_positions(),
            "broker": "dhan",
        }

    def _build_client(self) -> Any:
        try:
            from dhanhq import DhanContext, dhanhq  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install DhanHQ support with: pip install -e .[live]") from exc

        dhan_context = DhanContext(self.client_id, self.access_token)
        return dhanhq(dhan_context)

    def _instrument(self, symbol: str) -> Instrument:
        clean = symbol.upper()
        instrument = self.instruments.get(clean)
        if instrument is None or not instrument.security_id:
            raise RuntimeError(
                f"Dhan security_id missing for {clean}. Fill it in "
                f"{Path('instruments.dhan.csv').resolve()} before live trading."
            )
        return instrument


def _transaction_type(direction: Direction) -> str:
    return "BUY" if direction == Direction.LONG else "SELL"


def _product_type(product: str) -> str:
    if product == "MIS":
        return "INTRADAY"
    return product


def _correlation_id(prefix: str) -> str:
    return f"ds-{prefix}-{uuid4().hex[:16]}"


def _normalize_order_response(response: Any) -> dict[str, Any]:
    if isinstance(response, dict):
        order_id = response.get("orderId") or response.get("order_id") or response.get("data", {}).get("orderId")
        status = response.get("orderStatus") or response.get("order_status") or response.get("status", "PLACED")
        return {"order_id": str(order_id or ""), "status": str(status), "raw": response, "broker": "dhan"}
    return {"order_id": str(response), "status": "PLACED", "raw": response, "broker": "dhan"}
