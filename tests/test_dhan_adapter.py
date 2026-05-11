from __future__ import annotations

import os
import unittest

from trading_agent.config import BrokerConfig, load_config
from trading_agent.execution.dhan import DhanExecutionAdapter
from trading_agent.instruments import Instrument
from trading_agent.models import Direction, OrderPlan


class FakeDhanClient:
    def __init__(self) -> None:
        self.orders: list[dict[str, object]] = []

    def place_order(self, **kwargs: object) -> dict[str, object]:
        self.orders.append(kwargs)
        return {"orderId": f"order-{len(self.orders)}", "orderStatus": "PENDING"}

    def get_order_list(self) -> list[dict[str, object]]:
        return self.orders

    def get_positions(self) -> list[dict[str, object]]:
        return []


class DhanAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["DHAN_CLIENT_ID"] = "client"
        os.environ["DHAN_ACCESS_TOKEN"] = "token"

    def test_config_loads_dhan_defaults_from_yaml(self) -> None:
        config = load_config("config.yaml")

        self.assertEqual(config.broker.name, "dhan")
        self.assertEqual(config.broker.client_id_env, "DHAN_CLIENT_ID")
        self.assertEqual(config.broker.access_token_env, "DHAN_ACCESS_TOKEN")

    def test_dhan_adapter_places_limit_entry_and_manual_exits(self) -> None:
        client = FakeDhanClient()
        adapter = DhanExecutionAdapter(
            BrokerConfig(name="dhan", access_token_env="DHAN_ACCESS_TOKEN"),
            client=client,
            instruments={"RELIANCE": Instrument("RELIANCE", "1333", "NSE_EQ")},
        )
        plan = OrderPlan(
            symbol="RELIANCE",
            direction=Direction.LONG,
            quantity=10,
            entry=2500.0,
            stop_loss=2450.0,
            target=2600.0,
            product="MIS",
        )

        entry = adapter.place_entry_order(plan)
        exits = adapter.place_exit_orders(plan, entry["order_id"])

        self.assertEqual(entry["order_id"], "order-1")
        self.assertEqual(exits["stop_order_id"], "order-2")
        self.assertEqual(exits["target_order_id"], "order-3")
        self.assertEqual(client.orders[0]["product_type"], "INTRADAY")
        self.assertEqual(client.orders[0]["order_type"], "LIMIT")
        self.assertEqual(client.orders[1]["order_type"], "STOP_LOSS")


if __name__ == "__main__":
    unittest.main()
