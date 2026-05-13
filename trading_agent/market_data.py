from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

import yfinance as yf

from trading_agent.config import BrokerConfig
from trading_agent.models import Candle


class YFinanceMarketDataClient:
    """Free market data client using yfinance."""

    def fetch_historical(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str,
    ) -> list[Candle]:
        # Map internal intervals to yfinance intervals
        interval_map = {
            "1min": "1m",
            "5min": "5m",
            "15min": "15m",
            "30min": "30m",
            "1hour": "1h",
            "1day": "1d",
            "1week": "1wk",
            "1month": "1mo",
        }
        yf_interval = interval_map.get(interval, interval)

        ticker = yf.Ticker(f"{symbol}.NS" if not symbol.endswith((".NS", ".BO")) else symbol)
        df = ticker.history(start=from_date, end=to_date, interval=yf_interval)

        candles = []
        for _, row in df.iterrows():
            candles.append(
                Candle(
                    symbol=symbol.upper(),
                    timestamp=row.name.to_pydatetime(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                    interval=interval,
                )
            )
        return candles

    def fetch_latest(self, symbol: str) -> float | None:
        ticker = yf.Ticker(f"{symbol}.NS" if not symbol.endswith((".NS", ".BO")) else symbol)
        try:
            info = ticker.fast_info
            return float(info.last_price) if info.last_price else None
        except Exception:
            return None


class KiteMarketDataClient:
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
        self._instrument_token_by_symbol: dict[str, int] = {}

    def fetch_historical(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str,
    ) -> list[Candle]:
        instrument_token = self.instrument_token(symbol)
        rows = self.kite.historical_data(instrument_token, from_date, to_date, interval)
        return [_row_to_candle(symbol, interval, row) for row in rows]

    def instrument_token(self, symbol: str) -> int:
        clean = symbol.upper()
        if clean not in self._instrument_token_by_symbol:
            instruments = self.kite.instruments("NSE")
            self._instrument_token_by_symbol = {
                item["tradingsymbol"].upper(): int(item["instrument_token"])
                for item in instruments
                if item.get("tradingsymbol") and item.get("instrument_token")
            }
        if clean not in self._instrument_token_by_symbol:
            raise KeyError(f"NSE instrument token not found for {symbol}")
        return self._instrument_token_by_symbol[clean]


def _row_to_candle(symbol: str, interval: str, row: dict[str, Any]) -> Candle:
    return Candle(
        symbol=symbol.upper(),
        timestamp=row["date"],
        open=float(row["open"]),
        high=float(row["high"]),
        low=float(row["low"]),
        close=float(row["close"]),
        volume=int(row.get("volume", 0)),
        interval=interval,
    )
