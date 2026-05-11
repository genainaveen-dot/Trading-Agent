# Demand/Supply Trading Agent

V1 implementation of the demand/supply-zone trading. It includes a visual dashboard, paper execution, DhanHQ live broker support, risk controls, and REST endpoints.

Default mode is safe: `paper`, `live_enabled: false`.

## Quick Start

```powershell
python -m unittest discover -s tests
python -m trading_agent.api --config config.yaml
```

Open the dashboard:

[http://127.0.0.1:8080/](http://127.0.0.1:8080/)

Useful JSON endpoints:

- `GET /health`
- `GET /signals`
- `GET /positions`
- `GET /orders`
- `GET /risk`
- `GET /kill-switch`
- `POST /kill-switch` with `{"enabled": true, "reason": "manual stop"}`

## DhanHQ Setup

Install live broker dependencies:

```powershell
pip install -e ".[live]"
```

Put your Dhan credentials in `.env`:

```text
DHAN_CLIENT_ID=your_dhan_client_id
DHAN_ACCESS_TOKEN=your_dhan_access_token
```

The app loads `.env` automatically from:

```text
C:\Users\vic\Documents\New project\.env
```

The `.env` file is ignored by Git. Use `.env.example` as the safe template.

## Dhan Instrument IDs

Dhan places equity orders with `security_id`, not only symbols. Before live trading, fill:

[instruments.dhan.csv]

Example:

```csv
symbol,security_id,exchange_segment
RELIANCE,1333,NSE_EQ
TCS,11536,NSE_EQ
```

Do not guess `security_id` values. Verify them from Dhan’s instrument master or DhanHQ documentation/account tools.

## Live Trading Gate

Live orders are blocked unless all are true:

- `mode: live`
- `live_enabled: true`
- `broker.name: dhan`
- `.env` has valid `DHAN_CLIENT_ID` and `DHAN_ACCESS_TOKEN`
- `instruments.dhan.csv` has valid `security_id` values
- kill switch is off
- risk checks pass

Keep `mode: paper` until backtests and live-shadow checks are acceptable.

## Current Config

Default broker is Dhan:

```yaml
broker:
  name: dhan
  client_id_env: DHAN_CLIENT_ID
  access_token_env: DHAN_ACCESS_TOKEN
  instrument_map_path: instruments.dhan.csv
```

Risk defaults:

```yaml
risk:
  account_equity: 100000
  risk_per_trade_pct: 1.5
  max_daily_loss_pct: 4.5
  max_open_trades: 3
```

## Project Shape

- `trading_agent.strategy`: candle classification, zones, trend, curve, scoring, signals.
- `trading_agent.risk`: position sizing and trade rejection.
- `trading_agent.execution.dhan`: DhanHQ live order adapter.
- `trading_agent.execution.paper`: safe paper execution adapter.
- `trading_agent.api`: dashboard and REST status/control API.
- `tests`: unit coverage for strategy, risk, paper execution, and Dhan adapter behavior.

## Zerodha Note

A Zerodha Kite adapter still exists in `trading_agent.execution.kite`, but the active config is DhanHQ.
