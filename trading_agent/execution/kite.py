from __future__ import annotations

import os
from typing import Any

from trading_agent.config import BrokerConfig
from trading_agent.execution.base import ExecutionAdapter
from trading_agent.models import Direction, OrderPlan


class KiteExecutionAdapter(ExecutionAdapter):
    """Zerodha Kite adapter.

    This class imports kiteconnect lazily so tests and paper mode do not require
    broker dependencies. Use only after config gates have enabled live trading.
    """

    def __init__(self, config: BrokerConfig) -> None:
        try:
            from kiteconnect import KiteConnect  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install kiteconnect with: pip install -e .[live]") from exc

        api_key = os.environ.get(config.api_key_env)
        access_token = os.environ.get(config.access_token_env)
        if not api_key or not access_token:
            raise RuntimeError("Kite API key/access token environment variables are missing")
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)

    def place_entry_order(self, plan: OrderPlan) -> dict[str, Any]:
        transaction_type = (
            self.kite.TRANSACTION_TYPE_BUY
            if plan.direction == Direction.LONG
            else self.kite.TRANSACTION_TYPE_SELL
        )
        order_id = self.kite.place_order(
            variety=self.kite.VARIETY_REGULAR,
            exchange=self.kite.EXCHANGE_NSE,
            tradingsymbol=plan.symbol,
            transaction_type=transaction_type,
            quantity=plan.quantity,
            product=plan.product,
            order_type=self.kite.ORDER_TYPE_LIMIT,
            price=plan.entry,
            validity=self.kite.VALIDITY_DAY,
            tag="ds-agent-entry",
        )
        return {"order_id": order_id, "status": "PLACED"}

    def place_exit_orders(self, plan: OrderPlan, entry_order_id: str) -> dict[str, Any]:
        if plan.product == "CNC":
            return self._place_gtt_oco(plan, entry_order_id)
        return self._place_intraday_exit_orders(plan, entry_order_id)

    def reconcile(self) -> dict[str, Any]:
        return {"orders": self.kite.orders(), "positions": self.kite.positions()}

    def _place_intraday_exit_orders(self, plan: OrderPlan, entry_order_id: str) -> dict[str, Any]:
        exit_transaction = (
            self.kite.TRANSACTION_TYPE_SELL
            if plan.direction == Direction.LONG
            else self.kite.TRANSACTION_TYPE_BUY
        )
        stop_order_id = self.kite.place_order(
            variety=self.kite.VARIETY_REGULAR,
            exchange=self.kite.EXCHANGE_NSE,
            tradingsymbol=plan.symbol,
            transaction_type=exit_transaction,
            quantity=plan.quantity,
            product=plan.product,
            order_type=self.kite.ORDER_TYPE_SL,
            price=plan.stop_loss,
            trigger_price=plan.stop_loss,
            validity=self.kite.VALIDITY_DAY,
            tag="ds-agent-stop",
        )
        target_order_id = self.kite.place_order(
            variety=self.kite.VARIETY_REGULAR,
            exchange=self.kite.EXCHANGE_NSE,
            tradingsymbol=plan.symbol,
            transaction_type=exit_transaction,
            quantity=plan.quantity,
            product=plan.product,
            order_type=self.kite.ORDER_TYPE_LIMIT,
            price=plan.target,
            validity=self.kite.VALIDITY_DAY,
            tag="ds-agent-target",
        )
        return {
            "parent_order_id": entry_order_id,
            "stop_order_id": stop_order_id,
            "target_order_id": target_order_id,
            "oco_mode": "manual",
        }

    def _place_gtt_oco(self, plan: OrderPlan, entry_order_id: str) -> dict[str, Any]:
        exit_transaction = (
            self.kite.TRANSACTION_TYPE_SELL
            if plan.direction == Direction.LONG
            else self.kite.TRANSACTION_TYPE_BUY
        )
        trigger_id = self.kite.place_gtt(
            trigger_type=self.kite.GTT_TYPE_OCO,
            tradingsymbol=plan.symbol,
            exchange=self.kite.EXCHANGE_NSE,
            trigger_values=[plan.stop_loss, plan.target],
            last_price=plan.entry,
            orders=[
                {
                    "transaction_type": exit_transaction,
                    "quantity": plan.quantity,
                    "order_type": self.kite.ORDER_TYPE_LIMIT,
                    "product": plan.product,
                    "price": plan.stop_loss,
                },
                {
                    "transaction_type": exit_transaction,
                    "quantity": plan.quantity,
                    "order_type": self.kite.ORDER_TYPE_LIMIT,
                    "product": plan.product,
                    "price": plan.target,
                },
            ],
        )
        return {
            "parent_order_id": entry_order_id,
            "gtt_trigger_id": trigger_id,
            "oco_mode": "kite_gtt",
        }
