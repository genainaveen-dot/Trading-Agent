from __future__ import annotations

import unittest
from datetime import datetime, timedelta

from trading_agent.models import Candle, CandleKind, CurveState, TrendState, ZoneType
from trading_agent.strategy.candles import classify_candle
from trading_agent.strategy.curve import analyze_curve
from trading_agent.strategy.scoring import score_zone
from trading_agent.strategy.trend import analyze_trend
from trading_agent.strategy.zones import detect_zones, nearest_zones


def candle(index: int, open_: float, high: float, low: float, close: float) -> Candle:
    return Candle(
        symbol="TEST",
        timestamp=datetime(2026, 1, 1) + timedelta(minutes=index),
        open=open_,
        high=high,
        low=low,
        close=close,
    )


class StrategyRulesTest(unittest.TestCase):
    def test_classifies_exciting_base_and_neutral_candles(self) -> None:
        self.assertEqual(classify_candle(candle(1, 100, 107, 99, 106)), CandleKind.EXCITING)
        self.assertEqual(classify_candle(candle(2, 100, 102, 99, 100.5)), CandleKind.BASE)
        self.assertEqual(classify_candle(candle(3, 100, 102, 98, 102)), CandleKind.NEUTRAL)

    def test_detects_demand_zone_lines_from_dbr_pattern(self) -> None:
        candles = [
            candle(1, 106, 107, 99, 100),
            candle(2, 100, 101, 99.5, 100.4),
            candle(3, 100.5, 107, 100.4, 106),
        ]

        zones = detect_zones(candles)

        self.assertEqual(len(zones), 1)
        zone = zones[0]
        self.assertEqual(zone.pattern, "DBR")
        self.assertEqual(zone.zone_type, ZoneType.DEMAND)
        self.assertAlmostEqual(zone.proximal, 100.4)
        self.assertAlmostEqual(zone.distal, 99.5)

    def test_detects_supply_zone_lines_from_rbd_pattern(self) -> None:
        candles = [
            candle(1, 100, 107, 99, 106),
            candle(2, 105.8, 106.5, 105, 105.4),
            candle(3, 105.2, 105.3, 98, 99),
        ]

        zones = detect_zones(candles)

        self.assertEqual(len(zones), 1)
        zone = zones[0]
        self.assertEqual(zone.pattern, "RBD")
        self.assertEqual(zone.zone_type, ZoneType.SUPPLY)
        self.assertAlmostEqual(zone.proximal, 105.4)
        self.assertAlmostEqual(zone.distal, 106.5)

    def test_scores_fresh_strong_zone_at_seven(self) -> None:
        zones = detect_zones(
            [
                candle(1, 106, 107, 99, 100),
                candle(2, 100, 101, 99.5, 100.4),
                candle(3, 100.5, 107, 100.4, 106),
            ]
        )

        scored = score_zone(zones[0])

        self.assertEqual(scored.score, 7.0)

    def test_trend_uses_50_sma_direction(self) -> None:
        rising = [candle(i, i, i + 1, i - 1, 100 + i) for i in range(60)]
        falling = [candle(i, i, i + 1, i - 1, 200 - i) for i in range(60)]

        self.assertEqual(analyze_trend(rising), TrendState.UP)
        self.assertEqual(analyze_trend(falling), TrendState.DOWN)

    def test_curve_location_from_nearest_fresh_zones(self) -> None:
        candles = [
            candle(1, 106, 107, 99, 100),
            candle(2, 100, 101, 99.5, 100.4),
            candle(3, 100.5, 107, 100.4, 106),
            candle(4, 106, 107, 105, 106.4),
            candle(5, 106.2, 106.3, 101, 101.2),
        ]
        demand, supply = nearest_zones(candles, current_price=103)

        self.assertEqual(analyze_curve(100.8, demand, supply), CurveState.VERY_LOW)
        self.assertEqual(analyze_curve(103.0, demand, supply), CurveState.EQUILIBRIUM)
        self.assertEqual(analyze_curve(105.4, demand, supply), CurveState.VERY_HIGH)


if __name__ == "__main__":
    unittest.main()
