from __future__ import annotations

import argparse
import json
import threading
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from trading_agent.agent import TradingAgent
from trading_agent.config import load_config, load_watchlist, load_instrument_map, filter_watchlist_by_instruments
from trading_agent.dashboard import DASHBOARD_HTML
from trading_agent.market_data import YFinanceMarketDataClient
from trading_agent.models import MarketSegment
from trading_agent.utils import to_jsonable


class BackgroundScanner:
    """Background scanner that processes watchlist symbols periodically."""

    def __init__(self, agent: TradingAgent, interval_seconds: int = 300):
        self.agent = agent
        self.interval = interval_seconds
        self.market_data = YFinanceMarketDataClient()
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _run_loop(self) -> None:
        while self._running:
            try:
                self._scan_watchlists()
            except Exception as e:
                print(f"Scanner error: {e}")
            time.sleep(self.interval)

    def _scan_watchlists(self) -> None:
        # Get watchlists
        equity_map = load_instrument_map(self.agent.config.broker.instrument_map_path)
        commodity_map = load_instrument_map(self.agent.config.broker.commodity_instrument_map_path)

        equity_symbols = filter_watchlist_by_instruments(
            load_watchlist(self.agent.config.watchlist_path), equity_map
        )
        commodity_symbols = filter_watchlist_by_instruments(
            load_watchlist(self.agent.config.commodity_watchlist_path), commodity_map
        )
        index_symbols = load_watchlist(self.agent.config.index_watchlist_path)

        # Scan equity
        for symbol in equity_symbols:
            self._process_symbol(symbol, MarketSegment.EQUITY)

        # Scan commodities
        for symbol in commodity_symbols:
            self._process_symbol(symbol, MarketSegment.COMMODITY)

        # Scan indices
        for symbol in index_symbols:
            self._process_symbol(symbol, MarketSegment.INDEX)

    def _process_symbol(self, symbol: str, market_segment: MarketSegment) -> None:
        try:
            # Get timeframe preset
            preset = self.agent.config.timeframe_preset

            # Fetch candles for different timeframes
            now = datetime.now()
            days_back = 90 if preset == "swing" else 30

            # Fetch data
            htf_interval = "1day"
            itf_interval = "1hour"
            ltf_interval = "15min"

            htf_candles = self.market_data.fetch_historical(
                symbol, now - timedelta(days=days_back), now, htf_interval
            )
            itf_candles = self.market_data.fetch_historical(
                symbol, now - timedelta(days=14), now, itf_interval
            )
            ltf_candles = self.market_data.fetch_historical(
                symbol, now - timedelta(days=3), now, ltf_interval
            )

            if htf_candles and ltf_candles:
                last_price = ltf_candles[-1].close if ltf_candles else None
                self.agent.process_symbol(
                    symbol=symbol,
                    htf_candles=htf_candles,
                    itf_candles=itf_candles,
                    ltf_candles=ltf_candles,
                    last_price=last_price,
                    market_segment=market_segment,
                )
        except Exception as e:
            print(f"Error processing {symbol}: {e}")


class AgentApiHandler(BaseHTTPRequestHandler):
    agent: TradingAgent

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        snapshot = self.agent.state.snapshot()
        if path in {"/", "/dashboard"}:
            self._send_html(DASHBOARD_HTML)
        elif path == "/health":
            self._send(
                {
                    "status": "ok",
                    "mode": snapshot["mode"],
                    "broker": self.agent.config.broker.name,
                    "live_enabled": snapshot["live_enabled"],
                    "kill_switch_enabled": snapshot["kill_switch"]["enabled"],
                }
            )
        elif path == "/signals":
            self._send(snapshot["signals"])
        elif path == "/alerts":
            self._send(snapshot["alerts"])
        elif path == "/watchlists":
            equity_map = load_instrument_map(self.agent.config.broker.instrument_map_path)
            commodity_map = load_instrument_map(self.agent.config.broker.commodity_instrument_map_path)
            self._send(
                {
                    "equity": filter_watchlist_by_instruments(load_watchlist(self.agent.config.watchlist_path), equity_map),
                    "commodity": filter_watchlist_by_instruments(load_watchlist(self.agent.config.commodity_watchlist_path), commodity_map),
                    "index": load_watchlist(self.agent.config.index_watchlist_path),
                    "equity_instrument_map": self.agent.config.broker.instrument_map_path,
                    "commodity_instrument_map": self.agent.config.broker.commodity_instrument_map_path,
                }
            )
        elif path == "/positions":
            self._send(snapshot["positions"])
        elif path == "/orders":
            self._send(snapshot["orders"])
        elif path == "/risk":
            self._send(
                {
                    "risk_config": to_jsonable(self.agent.config.risk),
                    "daily_realized_pnl": self.agent.risk.daily_realized_pnl,
                    "decisions": snapshot["risk_decisions"],
                }
            )
        elif path == "/kill-switch":
            self._send(snapshot["kill_switch"])
        else:
            self._send({"error": "not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/scan-symbol":
            payload = self._read_json()
            symbol = str(payload.get("symbol", "")).upper()
            if not symbol:
                self._send({"error": "symbol required"}, status=400)
                return
            # Run scan for this symbol
            from datetime import datetime, timedelta
            from trading_agent.market_data import YFinanceMarketDataClient
            from trading_agent.models import MarketSegment

            try:
                md = YFinanceMarketDataClient()
                now = datetime.now()
                htf = md.fetch_historical(symbol, now - timedelta(days=90), now, "1day")
                itf = md.fetch_historical(symbol, now - timedelta(days=14), now, "1hour")
                ltf = md.fetch_historical(symbol, now - timedelta(days=3), now, "15min")
                if not ltf:
                    self._send({"signals": 0, "error": "no data"})
                    return

                # Determine market segment
                index_symbols = load_watchlist(self.agent.config.index_watchlist_path)
                if symbol in index_symbols:
                    market_segment = MarketSegment.INDEX
                else:
                    market_segment = MarketSegment.EQUITY

                self.agent.process_symbol(
                    symbol=symbol,
                    htf_candles=htf,
                    itf_candles=itf,
                    ltf_candles=ltf,
                    last_price=ltf[-1].close,
                    market_segment=market_segment,
                )
                self._send({"signals": len(self.agent.state.signals), "symbol": symbol})
            except Exception as e:
                self._send({"error": str(e)}, status=500)
            return
        elif path != "/kill-switch":
            self._send({"error": "not found"}, status=404)
            return
        payload = self._read_json()
        enabled = bool(payload.get("enabled", True))
        reason = str(payload.get("reason", "manual API update"))
        self.agent.state.kill_switch.set(enabled=enabled, reason=reason)
        self._send(to_jsonable(self.agent.state.kill_switch))

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def _send(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(to_jsonable(payload), indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def build_server(agent: TradingAgent, host: str, port: int) -> ThreadingHTTPServer:
    handler = type("BoundAgentApiHandler", (AgentApiHandler,), {"agent": agent})
    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the demand/supply trading agent API")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--scan-interval", type=int, default=300, help="Scanner interval in seconds (default: 300)")
    parser.add_argument("--no-scan", action="store_true", help="Disable background scanner")
    args = parser.parse_args()
    config = load_config(args.config)
    watchlist = load_watchlist(config.watchlist_path)
    agent = TradingAgent(config)

    # Start background scanner
    scanner = None
    if not args.no_scan:
        scanner = BackgroundScanner(agent, interval_seconds=args.scan_interval)
        scanner.start()
        print(f"Background scanner started (interval: {args.scan_interval}s)")

    server = build_server(agent, config.api.host, config.api.port)
    print(
        f"Trading agent API running on http://{config.api.host}:{config.api.port} "
        f"mode={config.mode} watchlist={len(watchlist)}"
    )
    server.serve_forever()
    if scanner:
        scanner.stop()


if __name__ == "__main__":
    main()
