from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Literal


class CandleKind(str, Enum):
    EXCITING = "exciting"
    BASE = "base"
    NEUTRAL = "neutral"


class Direction(str, Enum):
    LONG = "long"
    SHORT = "short"


class ZoneType(str, Enum):
    DEMAND = "demand"
    SUPPLY = "supply"


class TrendState(str, Enum):
    UP = "up"
    DOWN = "down"
    SIDEWAYS = "sideways"


class CurveState(str, Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    EQUILIBRIUM = "equilibrium"
    LOW = "low"
    VERY_LOW = "very_low"
    UNKNOWN = "unknown"


class EntryType(str, Enum):
    SET_AND_FORGET = "type_1_set_and_forget"
    CONFIRMATION_CLOSE_OPEN = "type_2_close_open"
    CONFIRMATION_LEAVE_ZONE = "type_3_leave_zone"


class MarketSegment(str, Enum):
    EQUITY = "equity"
    COMMODITY = "commodity"
    INDEX = "index"


@dataclass(frozen=True)
class Candle:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int = 0
    interval: str = ""

    @property
    def body(self) -> float:
        return abs(self.close - self.open)

    @property
    def range(self) -> float:
        return max(self.high - self.low, 0.0)

    @property
    def upper_body(self) -> float:
        return max(self.open, self.close)

    @property
    def lower_body(self) -> float:
        return min(self.open, self.close)

    @property
    def is_bullish(self) -> bool:
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        return self.close < self.open


@dataclass(frozen=True)
class Zone:
    symbol: str
    zone_type: ZoneType
    pattern: str
    proximal: float
    distal: float
    base_start: datetime
    base_end: datetime
    legin_time: datetime
    legout_time: datetime
    base_count: int
    tested_count: int = 0
    legout_strength: Literal["normal", "strong", "very_strong"] = "normal"
    has_gap: bool = False
    score: float = 0.0
    fresh: bool = True

    @property
    def top(self) -> float:
        return max(self.proximal, self.distal)

    @property
    def bottom(self) -> float:
        return min(self.proximal, self.distal)

    def contains_price(self, price: float) -> bool:
        return self.bottom <= price <= self.top


@dataclass(frozen=True)
class TradeSignal:
    symbol: str
    direction: Direction
    zone: Zone
    entry: float
    stop_loss: float
    target: float
    score: float
    entry_type: EntryType
    trend: TrendState
    curve: CurveState
    timeframe_preset: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    reason: str = ""


@dataclass(frozen=True)
class SwingAlert:
    symbol: str
    market_segment: MarketSegment
    direction: Direction
    entry: float
    stop_loss: float
    target: float
    score: float
    pattern: str
    trend: TrendState
    curve: CurveState
    message: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class OrderPlan:
    symbol: str
    direction: Direction
    quantity: int
    entry: float
    stop_loss: float
    target: float
    product: Literal["CNC", "MIS"]
    order_type: Literal["LIMIT"] = "LIMIT"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PositionState:
    symbol: str
    direction: Direction
    quantity: int
    entry_price: float
    stop_loss: float
    target: float
    product: str
    status: str = "open"
    broker_order_ids: list[str] = field(default_factory=list)
    realized_pnl: float = 0.0
    exit_price: float | None = None


@dataclass(frozen=True)
class RiskDecision:
    accepted: bool
    reason: str
    quantity: int = 0
    risk_amount: float = 0.0
    order_plan: OrderPlan | None = None


@dataclass(frozen=True)
class TimeframePreset:
    name: str
    htf: tuple[str, ...]
    itf: tuple[str, ...]
    ltf: tuple[str, ...]
    product: Literal["CNC", "MIS"]
    allow_short: bool


TIMEFRAME_PRESETS: dict[str, TimeframePreset] = {
    "swing": TimeframePreset(
        name="swing",
        htf=("week", "day"),
        itf=("day", "75minute"),
        ltf=("15minute",),
        product="CNC",
        allow_short=False,
    ),
    "intraday": TimeframePreset(
        name="intraday",
        htf=("day", "75minute"),
        itf=("15minute",),
        ltf=("5minute", "3minute"),
        product="MIS",
        allow_short=True,
    ),
}
