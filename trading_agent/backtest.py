from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from trading_agent.models import Candle, Direction, TradeSignal


def load_candles_csv(path: str | Path, symbol: str, interval: str) -> list[Candle]:
    candles: list[Candle] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            candles.append(
                Candle(
                    symbol=symbol.upper(),
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=int(float(row.get("volume", 0) or 0)),
                    interval=interval,
                )
            )
    return candles


def simulate_signal(signal: TradeSignal, future_candles: list[Candle]) -> dict[str, float | str]:
    for candle in future_candles:
        if signal.direction == Direction.LONG:
            if candle.low <= signal.stop_loss:
                return {"outcome": "stop", "r_multiple": -1.0, "exit": signal.stop_loss}
            if candle.high >= signal.target:
                return {"outcome": "target", "r_multiple": 2.0, "exit": signal.target}
        else:
            if candle.high >= signal.stop_loss:
                return {"outcome": "stop", "r_multiple": -1.0, "exit": signal.stop_loss}
            if candle.low <= signal.target:
                return {"outcome": "target", "r_multiple": 2.0, "exit": signal.target}
    return {"outcome": "open", "r_multiple": 0.0, "exit": future_candles[-1].close if future_candles else signal.entry}
