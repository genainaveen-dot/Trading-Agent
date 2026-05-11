from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BrokerConfig:
    name: str = "dhan"
    api_key_env: str = "KITE_API_KEY"
    client_id_env: str = "DHAN_CLIENT_ID"
    access_token_env: str = "KITE_ACCESS_TOKEN"
    instrument_map_path: str = "instruments.dhan.csv"


@dataclass(frozen=True)
class RiskConfig:
    account_equity: float = 1_000_000.0
    risk_per_trade_pct: float = 1.5
    max_daily_loss_pct: float = 4.5
    max_open_trades: int = 3
    stop_buffer_pct: float = 0.05
    max_slippage_pct: float = 0.15
    tick_size: float = 0.05


@dataclass(frozen=True)
class StrategyConfig:
    target_r_multiple: float = 2.0
    sma_period: int = 50
    trend_lookback: int = 7
    max_base_candles: int = 6
    freshness_touch_limit: int = 2


@dataclass(frozen=True)
class ApiConfig:
    host: str = "127.0.0.1"
    port: int = 8080


@dataclass(frozen=True)
class AppConfig:
    mode: str = "paper"
    live_enabled: bool = False
    timeframe_preset: str = "swing"
    watchlist_path: str = "watchlist.txt"
    env_file: str = ".env"
    broker: BrokerConfig = BrokerConfig()
    risk: RiskConfig = RiskConfig()
    strategy: StrategyConfig = StrategyConfig()
    api: ApiConfig = ApiConfig()


def load_config(path: str | Path = "config.yaml") -> AppConfig:
    config_path = Path(path)
    raw = _load_mapping(config_path) if config_path.exists() else {}
    env_file = str(raw.get("env_file", ".env"))
    load_env_file(_resolve_relative(config_path, env_file))
    return AppConfig(
        mode=str(raw.get("mode", "paper")),
        live_enabled=bool(raw.get("live_enabled", False)),
        timeframe_preset=str(raw.get("timeframe_preset", "swing")),
        watchlist_path=str(raw.get("watchlist_path", "watchlist.txt")),
        env_file=env_file,
        broker=BrokerConfig(**_section(raw, "broker")),
        risk=RiskConfig(**_section(raw, "risk")),
        strategy=StrategyConfig(**_section(raw, "strategy")),
        api=ApiConfig(**_section(raw, "api")),
    )


def load_env_file(path: str | Path) -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_watchlist(path: str | Path) -> list[str]:
    watchlist_path = Path(path)
    if not watchlist_path.exists():
        return []
    symbols: list[str] = []
    for line in watchlist_path.read_text(encoding="utf-8").splitlines():
        clean = line.strip().upper()
        if clean and not clean.startswith("#"):
            symbols.append(clean)
    return symbols


def _resolve_relative(base_file: Path, maybe_relative: str) -> Path:
    candidate = Path(maybe_relative)
    if candidate.is_absolute():
        return candidate
    return base_file.parent / candidate


def _section(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key, {})
    return value if isinstance(value, dict) else {}


def _load_mapping(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"{path} must contain a mapping")
        return loaded
    except ModuleNotFoundError:
        return _parse_simple_yaml(text)


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Small YAML subset parser for the provided config shape.

    It supports top-level scalar keys plus one indentation level of mappings.
    Install PyYAML for richer configuration syntax.
    """

    root: dict[str, Any] = {}
    current_section: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line:
            continue
        if not raw_line.startswith(" ") and line.endswith(":"):
            key = line[:-1].strip()
            current_section = {}
            root[key] = current_section
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed = _parse_scalar(value.strip())
        if raw_line.startswith(" ") and current_section is not None:
            current_section[key.strip()] = parsed
        else:
            current_section = None
            root[key.strip()] = parsed
    return root


def _parse_scalar(value: str) -> Any:
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "none", "~"}:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value
