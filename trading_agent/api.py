from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from trading_agent.agent import TradingAgent
from trading_agent.config import load_config, load_watchlist
from trading_agent.dashboard import DASHBOARD_HTML
from trading_agent.utils import to_jsonable


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
        if path != "/kill-switch":
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
    args = parser.parse_args()
    config = load_config(args.config)
    watchlist = load_watchlist(config.watchlist_path)
    agent = TradingAgent(config)
    server = build_server(agent, config.api.host, config.api.port)
    print(
        f"Trading agent API running on http://{config.api.host}:{config.api.port} "
        f"mode={config.mode} watchlist={len(watchlist)}"
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
