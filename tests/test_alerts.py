from __future__ import annotations

import unittest
from datetime import UTC, datetime

from trading_agent.alerts import SwingAlertAgent
from trading_agent.models import (
    CurveState,
    Direction,
    EntryType,
    MarketSegment,
    TradeSignal,
    TrendState,
)
from trading_agent.strategy.scoring import score_zone
from trading_agent.strategy.zones import detect_zones
from tests.test_strategy_rules import candle


class SwingAlertAgentTest(unittest.TestCase):
    def test_builds_commodity_swing_alert_from_signal(self) -> None:
        zone = score_zone(
            detect_zones(
                [
                    candle(1, 106, 107, 99, 100),
                    candle(2, 100, 101, 99.5, 100.4),
                    candle(3, 100.5, 107, 100.4, 106),
                ]
            )[0]
        )
        signal = TradeSignal(
            symbol="CRUDEOIL",
            direction=Direction.LONG,
            zone=zone,
            entry=100.4,
            stop_loss=99.5,
            target=102.2,
            score=7,
            entry_type=EntryType.SET_AND_FORGET,
            trend=TrendState.UP,
            curve=CurveState.LOW,
            timeframe_preset="swing",
            created_at=datetime.now(UTC),
        )

        alert = SwingAlertAgent().build_alert(signal, MarketSegment.COMMODITY)

        self.assertEqual(alert.market_segment, MarketSegment.COMMODITY)
        self.assertEqual(alert.symbol, "CRUDEOIL")
        self.assertIn("COMMODITY swing LONG alert", alert.message)
        self.assertEqual(alert.pattern, "DBR")


if __name__ == "__main__":
    unittest.main()
