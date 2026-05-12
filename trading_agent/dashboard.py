from __future__ import annotations


DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Trading Agent Dashboard</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fa;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #667085;
      --line: #d8dee8;
      --soft-line: #edf0f5;
      --green: #0f8a5f;
      --red: #c43b3b;
      --amber: #a56508;
      --blue: #2458b8;
      --nav: #1f2933;
      --shadow: 0 1px 2px rgba(16, 24, 40, 0.08);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    * { box-sizing: border-box; }
    body { margin: 0; min-width: 320px; background: var(--bg); color: var(--ink); }
    button, input { font: inherit; }

    .app { min-height: 100vh; display: grid; grid-template-columns: 244px minmax(0, 1fr); }
    .sidebar { background: var(--nav); color: #f6f8fb; padding: 22px 18px; display: flex; flex-direction: column; gap: 22px; }
    .brand { display: grid; gap: 4px; }
    .brand h1 { margin: 0; font-size: 18px; line-height: 1.25; letter-spacing: 0; }
    .brand span { color: #b9c1cc; font-size: 13px; }

    .nav { display: grid; gap: 6px; }
    .nav button {
      min-height: 38px;
      border: 0;
      border-radius: 6px;
      background: transparent;
      color: #dbe2eb;
      text-align: left;
      padding: 10px 12px;
      cursor: pointer;
    }
    .nav button.active, .nav button:hover { background: #33414f; color: #ffffff; }

    .content { min-width: 0; padding: 24px; display: grid; gap: 18px; align-content: start; }
    .topbar { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }
    .title h2 { margin: 0; font-size: 24px; line-height: 1.2; letter-spacing: 0; }
    .title p { margin: 4px 0 0; color: var(--muted); font-size: 14px; }
    .toolbar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }

    .status-pill, .button {
      min-height: 36px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--ink);
      padding: 8px 12px;
      box-shadow: var(--shadow);
      font-size: 13px;
    }
    .button { cursor: pointer; }
    .button:hover { border-color: #b9c4d3; }
    .button.danger { color: #ffffff; background: var(--red); border-color: var(--red); }
    .button.safe { color: #ffffff; background: var(--green); border-color: var(--green); }

    .grid { display: grid; grid-template-columns: repeat(4, minmax(150px, 1fr)); gap: 12px; }
    .metric, .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; box-shadow: var(--shadow); }
    .metric { padding: 14px; min-height: 94px; display: grid; align-content: space-between; gap: 12px; }
    .metric label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0; }
    .metric strong { font-size: 22px; line-height: 1.1; letter-spacing: 0; }
    .metric small { color: var(--muted); font-size: 12px; }

    .panel { min-width: 0; overflow: hidden; }
    .panel-header {
      min-height: 48px;
      padding: 12px 14px;
      border-bottom: 1px solid var(--soft-line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }
    .panel-header h3 { margin: 0; font-size: 15px; letter-spacing: 0; }
    .panel-header span { color: var(--muted); font-size: 12px; }

    .section-grid { display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.85fr); gap: 12px; }
    .tab-page { display: none; gap: 12px; }
    .tab-page.active { display: grid; }

    table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    th, td {
      text-align: left;
      padding: 11px 14px;
      border-bottom: 1px solid var(--soft-line);
      font-size: 13px;
      vertical-align: top;
      word-break: break-word;
    }
    th { color: var(--muted); font-size: 12px; font-weight: 600; background: #fbfcfe; }
    tr:last-child td { border-bottom: 0; }

    .empty { min-height: 120px; display: grid; place-items: center; color: var(--muted); font-size: 14px; padding: 18px; text-align: center; }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 3px 8px;
      border-radius: 999px;
      font-size: 12px;
      background: #eef2f7;
      color: #344054;
      white-space: nowrap;
    }
    .badge.green { background: #e8f6ef; color: var(--green); }
    .badge.red { background: #faecec; color: var(--red); }
    .badge.amber { background: #fff4df; color: var(--amber); }
    .badge.blue { background: #eaf0ff; color: var(--blue); }

    .risk-list, .symbol-list { display: grid; gap: 1px; background: var(--soft-line); }
    .risk-row, .symbol-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; background: var(--panel); padding: 12px 14px; font-size: 13px; }
    .risk-row span, .symbol-row span { color: var(--muted); }
    .risk-row strong, .symbol-row strong { font-size: 13px; text-align: right; }
    .mono { font-family: "Cascadia Mono", Consolas, monospace; }

    @media (max-width: 980px) {
      .app { grid-template-columns: 1fr; }
      .sidebar { padding: 16px; }
      .nav { display: flex; overflow-x: auto; }
      .nav button { white-space: nowrap; }
      .content { padding: 16px; }
      .grid, .section-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">
        <h1>Demand/Supply Agent</h1>
        <span>Dhan swing alert console</span>
      </div>
      <nav class="nav" aria-label="Dashboard tabs">
        <button class="active" data-tab="equity" type="button">Equity</button>
        <button data-tab="commodity" type="button">Commodity</button>
        <button data-tab="alerts" type="button">Swing Alerts</button>
        <button data-tab="orders" type="button">Orders & Risk</button>
      </nav>
    </aside>

    <main class="content">
      <div class="topbar">
        <div class="title">
          <h2>Trading Agent Dashboard</h2>
          <p id="subtitle">Loading agent state</p>
        </div>
        <div class="toolbar">
          <span class="status-pill" id="updated">Last update: --</span>
          <button class="button" id="refresh" type="button">Refresh</button>
          <button class="button danger" id="kill" type="button">Kill Switch</button>
        </div>
      </div>

      <section class="grid" aria-label="Agent metrics">
        <div class="metric"><label>Mode</label><strong id="metric-mode">--</strong><small id="metric-live">--</small></div>
        <div class="metric"><label>Broker</label><strong id="metric-broker">--</strong><small>Dhan credentials from .env</small></div>
        <div class="metric"><label>Swing Alerts</label><strong id="metric-alerts">0</strong><small>Latest 100 retained</small></div>
        <div class="metric"><label>Kill Switch</label><strong id="metric-kill">--</strong><small id="metric-kill-reason">--</small></div>
      </section>

      <section class="tab-page active" id="tab-equity">
        <div class="section-grid">
          <div class="panel">
            <div class="panel-header"><h3>Equity Signals</h3><span>NSE swing setup stream</span></div>
            <div id="equity-signals-body"></div>
          </div>
          <div class="panel">
            <div class="panel-header"><h3>Equity Watchlist</h3><span id="equity-map-path">Dhan map</span></div>
            <div class="symbol-list" id="equity-watchlist-body"></div>
          </div>
        </div>
      </section>

      <section class="tab-page" id="tab-commodity">
        <div class="section-grid">
          <div class="panel">
            <div class="panel-header"><h3>Commodity Alerts</h3><span>MCX swing alert stream</span></div>
            <div id="commodity-alerts-body"></div>
          </div>
          <div class="panel">
            <div class="panel-header"><h3>Commodity Watchlist</h3><span id="commodity-map-path">Dhan map</span></div>
            <div class="symbol-list" id="commodity-watchlist-body"></div>
          </div>
        </div>
      </section>

      <section class="tab-page" id="tab-alerts">
        <div class="panel">
          <div class="panel-header"><h3>Swing Trading Alerts</h3><span>Generated from demand/supply signals</span></div>
          <div id="alerts-body"></div>
        </div>
      </section>

      <section class="tab-page" id="tab-orders">
        <div class="section-grid">
          <div class="panel">
            <div class="panel-header"><h3>Orders</h3><span>Broker or paper responses</span></div>
            <div id="orders-body"></div>
          </div>
          <div class="panel">
            <div class="panel-header"><h3>Risk Controls</h3><span>Active config</span></div>
            <div class="risk-list" id="risk-body"></div>
          </div>
        </div>
      </section>
    </main>
  </div>

  <script>
    const fmt = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 });
    const money = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 });
    const $ = (id) => document.getElementById(id);

    document.querySelectorAll(".nav button").forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelectorAll(".nav button").forEach((item) => item.classList.remove("active"));
        document.querySelectorAll(".tab-page").forEach((page) => page.classList.remove("active"));
        button.classList.add("active");
        $(`tab-${button.dataset.tab}`).classList.add("active");
      });
    });

    async function fetchJson(path, options) {
      const response = await fetch(path, options);
      if (!response.ok) throw new Error(`${path} returned ${response.status}`);
      return response.json();
    }

    async function loadDashboard() {
      const [health, signals, positions, orders, risk, kill, alerts, watchlists] = await Promise.all([
        fetchJson("/health"),
        fetchJson("/signals"),
        fetchJson("/positions"),
        fetchJson("/orders"),
        fetchJson("/risk"),
        fetchJson("/kill-switch"),
        fetchJson("/alerts"),
        fetchJson("/watchlists")
      ]);

      $("subtitle").textContent = `${health.mode.toUpperCase()} mode - ${health.broker || "paper"} broker - ${health.live_enabled ? "live orders enabled" : "live orders disabled"}`;
      $("updated").textContent = `Last update: ${new Date().toLocaleTimeString()}`;
      $("metric-mode").textContent = health.mode.toUpperCase();
      $("metric-live").textContent = health.live_enabled ? "Live execution enabled" : "Paper or alert-only execution";
      $("metric-broker").textContent = (health.broker || "paper").toUpperCase();
      $("metric-alerts").textContent = fmt.format(alerts.length);
      $("metric-kill").textContent = kill.enabled ? "ON" : "OFF";
      $("metric-kill").style.color = kill.enabled ? "var(--red)" : "var(--green)";
      $("metric-kill-reason").textContent = kill.reason || "No active stop reason";
      $("kill").textContent = kill.enabled ? "Resume Agent" : "Kill Switch";
      $("kill").className = kill.enabled ? "button safe" : "button danger";

      renderSignals(signals.filter((signal) => !signal.market_segment || signal.market_segment === "equity"), "equity-signals-body");
      renderAlerts(alerts, "alerts-body");
      renderAlerts(alerts.filter((alert) => alert.market_segment === "commodity"), "commodity-alerts-body");
      renderWatchlist(watchlists.equity || [], "equity-watchlist-body");
      renderWatchlist(watchlists.commodity || [], "commodity-watchlist-body");
      $("equity-map-path").textContent = watchlists.equity_instrument_map || "";
      $("commodity-map-path").textContent = watchlists.commodity_instrument_map || "";
      renderOrders(orders);
      renderRisk(risk, kill, positions);
    }

    function renderSignals(signals, targetId) {
      if (!signals.length) {
        $(targetId).innerHTML = `<div class="empty">No signals recorded yet. The swing alert agent will populate this after scans.</div>`;
        return;
      }
      const rows = signals.slice(-12).reverse().map((signal) => `
        <tr>
          <td><strong>${escapeHtml(signal.symbol)}</strong><br><span class="mono">${escapeHtml(signal.zone.pattern)}</span></td>
          <td>${badge(signal.direction, signal.direction === "long" ? "green" : "red")}</td>
          <td>${fmt.format(signal.score)}<br><span class="mono">${escapeHtml(signal.entry_type)}</span></td>
          <td>${money.format(signal.entry)}<br><span>SL ${money.format(signal.stop_loss)}</span></td>
          <td>${money.format(signal.target)}<br><span>${escapeHtml(signal.curve)}</span></td>
        </tr>`).join("");
      $(targetId).innerHTML = `<table><thead><tr><th>Symbol</th><th>Side</th><th>Score</th><th>Entry</th><th>Target</th></tr></thead><tbody>${rows}</tbody></table>`;
    }

    function renderAlerts(alerts, targetId) {
      if (!alerts.length) {
        $(targetId).innerHTML = `<div class="empty">No swing alerts yet.</div>`;
        return;
      }
      const rows = alerts.slice(-20).reverse().map((alert) => `
        <tr>
          <td><strong>${escapeHtml(alert.symbol)}</strong><br>${badge(alert.market_segment, alert.market_segment === "commodity" ? "amber" : "blue")}</td>
          <td>${badge(alert.direction, alert.direction === "long" ? "green" : "red")}<br><span class="mono">${escapeHtml(alert.pattern)}</span></td>
          <td>${fmt.format(alert.score)}<br><span>${escapeHtml(alert.trend)}</span></td>
          <td>${money.format(alert.entry)}<br><span>SL ${money.format(alert.stop_loss)}</span></td>
          <td>${escapeHtml(alert.message)}</td>
        </tr>`).join("");
      $(targetId).innerHTML = `<table><thead><tr><th>Symbol</th><th>Setup</th><th>Score</th><th>Price</th><th>Message</th></tr></thead><tbody>${rows}</tbody></table>`;
    }

    function renderWatchlist(symbols, targetId) {
      if (!symbols.length) {
        $(targetId).innerHTML = `<div class="empty">No symbols configured.</div>`;
        return;
      }
      $(targetId).innerHTML = symbols.map((symbol, index) => `
        <div class="symbol-row"><span>${index + 1}</span><strong>${escapeHtml(symbol)}</strong></div>
      `).join("");
    }

    function renderOrders(orders) {
      if (!orders.length) {
        $("orders-body").innerHTML = `<div class="empty">No order events yet.</div>`;
        return;
      }
      const rows = orders.slice(-10).reverse().map((event) => {
        const response = event.broker_response || {};
        const plan = event.plan || {};
        return `<tr><td><strong>${escapeHtml(plan.symbol || "--")}</strong><br>${escapeHtml(response.order_id || response.gtt_trigger_id || response.parent_order_id || "--")}</td><td>${badge(response.status || response.oco_mode || "event", response.status === "COMPLETE" ? "green" : "blue")}</td><td>${fmt.format(plan.quantity || 0)}<br><span>${escapeHtml(plan.product || "--")}</span></td></tr>`;
      }).join("");
      $("orders-body").innerHTML = `<table><thead><tr><th>Order</th><th>Status</th><th>Qty</th></tr></thead><tbody>${rows}</tbody></table>`;
    }

    function renderRisk(risk, kill, positions) {
      const config = risk.risk_config || {};
      const rows = [
        ["Account equity", money.format(config.account_equity || 0)],
        ["Risk per trade", `${config.risk_per_trade_pct || 0}%`],
        ["Max daily loss", `${config.max_daily_loss_pct || 0}%`],
        ["Open positions", fmt.format((positions || []).filter((p) => p.status === "open").length)],
        ["Daily realized P&L", money.format(risk.daily_realized_pnl || 0)],
        ["Kill switch", kill.enabled ? "Enabled" : "Disabled"]
      ];
      $("risk-body").innerHTML = rows.map(([label, value]) => `<div class="risk-row"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join("");
    }

    function badge(text, color) {
      return `<span class="badge ${color || ""}">${escapeHtml(text)}</span>`;
    }

    async function toggleKillSwitch() {
      const current = $("metric-kill").textContent === "ON";
      await fetchJson("/kill-switch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(current ? { enabled: false, reason: "resumed from dashboard" } : { enabled: true, reason: "stopped from dashboard" })
      });
      await loadDashboard();
    }

    function escapeHtml(value) {
      return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
    }

    $("refresh").addEventListener("click", loadDashboard);
    $("kill").addEventListener("click", toggleKillSwitch);
    loadDashboard().catch((error) => { $("subtitle").textContent = error.message; });
    setInterval(() => loadDashboard().catch(() => {}), 5000);
  </script>
</body>
</html>
"""
