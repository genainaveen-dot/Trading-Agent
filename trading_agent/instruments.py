from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Instrument:
    symbol: str
    security_id: str
    exchange_segment: str = "NSE_EQ"


def load_dhan_instruments(path: str | Path) -> dict[str, Instrument]:
    instrument_path = Path(path)
    if not instrument_path.exists():
        return {}
    with instrument_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        instruments: dict[str, Instrument] = {}
        for row in reader:
            symbol = (row.get("symbol") or "").strip().upper()
            security_id = (row.get("security_id") or "").strip()
            exchange_segment = (row.get("exchange_segment") or "NSE_EQ").strip() or "NSE_EQ"
            if not symbol:
                continue
            instruments[symbol] = Instrument(
                symbol=symbol,
                security_id=security_id,
                exchange_segment=exchange_segment,
            )
        return instruments
