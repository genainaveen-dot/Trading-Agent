from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import UTC, datetime

from trading_agent.config import RiskConfig
from trading_agent.execution.paper import PaperExecutionAdapter
from trading_agent.models import Direction, EntryType, TradeSignal, TrendState, CurveState
from trading_agent.risk import RiskManager
from trading_agent.strategy.scoring import score_zone
from trading_agent.strategy.zones import detect_zones
from tests.test_strategy_rules import candle


def signal(direction: Direction = Direction.LONG) -> TradeSignal:
    zone = score_zone(
        detect_zones(
            [
                candle(1, 106, 107, 99, 100),
                candle(2, 100, 101, 99.5, 100.4),
                candle(3, 100.5, 107, 100.4, 106),
            ]
        )[0]
    )
    if direction == Direction.SHORT:
        zone = replace(zone, zone_type=zone.zone_type, proximal=100, distal=105, score=7)
    return TradeSignal(
        symbol="TEST",
        direction=direction,
        zone=zone,
        entry=100,
        stop_loss=95 if direction == Direction.LONG else 105,
        target=110 if direction == Direction.LONG else 90,
        score=7,
        entry_type=EntryType.SET_AND_FORGET,
        trend=TrendState.UP if direction == Direction.LONG else TrendState.DOWN,
        curve=CurveState.LOW if direction == Direction.LONG else CurveState.HIGH,
        timeframe_preset="intraday",
        created_at=datetime.now(UTC),
    )


class RiskAndExecutionTest(unittest.TestCase):
    def test_sizes_position_from_risk_budget(self) -> None:
        manager = RiskManager(RiskConfig(account_equity=100_000, risk_per_trade_pct=1.5))

        decision = manager.evaluate(
            signal(),
            open_positions=[],
            product="MIS",
            live_enabled=True,
        )

        self.assertTrue(decision.accepted)
        self.assertIsNotNone(decision.order_plan)
        self.assertEqual(decision.quantity, 297)
        self.assertLessEqual(decision.risk_amount, 1500)

    def test_rejects_when_kill_switch_enabled(self) -> None:
        manager = RiskManager()

        decision = manager.evaluate(
            signal(),
            open_positions=[],
            product="MIS",
            live_enabled=True,
            kill_switch_enabled=True,
        )

        self.assertFalse(decision.accepted)
        self.assertIn("kill switch", decision.reason)

    def test_rejects_cash_equity_short(self) -> None:
        manager = RiskManager()

        decision = manager.evaluate(
            signal(Direction.SHORT),
            open_positions=[],
            product="CNC",
            live_enabled=True,
        )

        self.assertFalse(decision.accepted)
        self.assertIn("shorts", decision.reason)

    def test_paper_execution_creates_entry_and_exit_orders(self) -> None:
        manager = RiskManager()
        decision = manager.evaluate(signal(), [], "MIS", live_enabled=True)
        adapter = PaperExecutionAdapter()

        entry = adapter.place_entry_order(decision.order_plan)  # type: ignore[arg-type]
        exits = adapter.place_exit_orders(decision.order_plan, entry["order_id"])  # type: ignore[arg-type]

        self.assertEqual(entry["status"], "COMPLETE")
        self.assertEqual(exits["status"], "OPEN")
        self.assertEqual(len(adapter.reconcile()["orders"]), 2)


if __name__ == "__main__":
    unittest.main()
