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
    .button.primary { color: #ffffff; background: var(--blue); border-color: var(--blue); }
    .button.primary:hover { background: #1d4a9b; }

    .symbol-select {
      min-height: 36px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--ink);
      padding: 8px 12px;
      font-size: 13px;
      min-width: 180px;
    }

    .watchlist-filter-select {
      border: 1px solid var(--line);
      border-radius: 4px;
      background: var(--panel);
      color: var(--ink);
      padding: 4px 8px;
      font-size: 12px;
      max-width: 140px;
    }

    .scan-toolbar {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
      padding: 12px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }

    .scan-result {
      display: none;
      margin-bottom: 12px;
      padding: 12px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      font-size: 13px;
    }
    .scan-result.show { display: block; }
    .scan-result.success { border-left: 4px solid var(--green); }
    .scan-result.error { border-left: 4px solid var(--red); }
    .scan-result .signal-details { margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--soft-line); }
    .scan-result .signal-row { display: flex; justify-content: space-between; padding: 4px 0; }
    .scan-result .signal-label { color: var(--muted); }
    .scan-result .signal-value { font-weight: 600; }

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
    .symbol-row.active-filter { background: #eaf0ff; border-left: 3px solid var(--blue); }
    .filter-clear { cursor: pointer; color: var(--muted); font-size: 12px; margin-left: 8px; padding: 2px 6px; border-radius: 4px; }
    .filter-clear:hover { background: #d0e0ff; color: var(--blue); }
    .filter-badge { display: inline-flex; align-items: center; gap: 6px; background: var(--blue); color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; margin-bottom: 8px; }
    .filter-badge .clear { cursor: pointer; opacity: 0.8; }
    .filter-badge .clear:hover { opacity: 1; }
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
        <button data-tab="index" type="button">Index</button>
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
        <div class="scan-toolbar">
          <select id="equity-symbol-select" class="symbol-select">
            <option value="">Select Equity Symbol</option>
          </select>
          <button class="button primary" id="equity-scan" type="button">Run Scan</button>
        </div>
        <div class="scan-result" id="equity-scan-result"></div>
        <div class="section-grid">
          <div class="panel">
            <div class="panel-header"><h3>Equity Signals</h3><span>NSE swing setup stream</span></div>
            <div id="equity-signals-body"></div>
          </div>
          <div class="panel">
            <div class="panel-header">
              <h3>Equity Watchlist</h3>
              <div>
                <select id="equity-watchlist-filter" class="watchlist-filter-select" onchange="filterEquityBySymbol(this.value)">
                  <option value="">All Symbols</option>
                </select>
                <span id="equity-map-path">Dhan map</span>
              </div>
            </div>
            <div class="symbol-list" id="equity-watchlist-body"></div>
          </div>
        </div>
      </section>

      <section class="tab-page" id="tab-commodity">
        <div class="scan-toolbar">
          <select id="commodity-symbol-select" class="symbol-select">
            <option value="">Select Commodity Symbol</option>
          </select>
          <button class="button primary" id="commodity-scan" type="button">Run Scan</button>
        </div>
        <div class="scan-result" id="commodity-scan-result"></div>
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

      <section class="tab-page" id="tab-index">
        <div class="scan-toolbar">
          <select id="index-symbol-select" class="symbol-select">
            <option value="">Select Index Symbol</option>
          </select>
          <button class="button primary" id="index-scan" type="button">Run Scan</button>
        </div>
        <div class="scan-result" id="index-scan-result"></div>
        <div class="section-grid">
          <div class="panel">
            <div class="panel-header"><h3>Index Signals</h3><span>NSE index swing setup stream</span></div>
            <div id="index-signals-body"></div>
          </div>
          <div class="panel">
            <div class="panel-header"><h3>Index Watchlist</h3><span>Nifty, BankNifty, Finnifty</span></div>
            <div class="symbol-list" id="index-watchlist-body"></div>
          </div>
        </div>
      </section>

      <section class="tab-page" id="tab-alerts">
        <div class="panel">
          <div class="panel-header">
            <h3>Swing Trading Alerts</h3>
            <div>
              <select id="alerts-filter" class="watchlist-filter-select" onchange="filterAlertsBySegment(this.value)">
                <option value="">All Segments</option>
                <option value="equity">Equity</option>
                <option value="commodity">Commodity</option>
              </select>
            </div>
          </div>
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

      const equitySignals = getFilteredSignals(signals.filter((signal) => !signal.market_segment || signal.market_segment === "equity"), "equity");
      const commodityAlerts = getFilteredAlerts(alerts.filter((alert) => alert.market_segment === "commodity"), "commodity");
      const indexSignals = getFilteredSignals(signals.filter((signal) => signal.market_segment === "index"), "index");

      // Filter alerts for alerts tab
      let filteredAlerts = alerts;
      if (filters.alerts) {
        filteredAlerts = alerts.filter(a => a.market_segment === filters.alerts);
      }

      renderSignals(equitySignals, "equity-signals-body", "equity");
      renderAlerts(filteredAlerts, "alerts-body");
      renderAlerts(commodityAlerts, "commodity-alerts-body", "commodity");
      renderSignals(indexSignals, "index-signals-body", "index");
      renderWatchlist(watchlists.equity || [], "equity-watchlist-body", "equity");
      renderWatchlist(watchlists.commodity || [], "commodity-watchlist-body", "commodity");
      renderWatchlist(watchlists.index || [], "index-watchlist-body", "index");
      $("equity-map-path").textContent = watchlists.equity_instrument_map || "";
      $("commodity-map-path").textContent = watchlists.commodity_instrument_map || "";
      renderOrders(orders);
      renderRisk(risk, kill, positions);

      // Restore filter dropdown selected values
      if (filters.equity) {
        $("equity-watchlist-filter").value = filters.equity;
      }
      if (filters.alerts) {
        $("alerts-filter").value = filters.alerts;
      }

      // Populate equity symbol select
      const equitySelect = $("equity-symbol-select");
      equitySelect.innerHTML = '<option value="">Select Equity Symbol</option>';
      (watchlists.equity || []).forEach(sym => {
        const opt = document.createElement("option");
        opt.value = sym;
        opt.textContent = sym;
        equitySelect.appendChild(opt);
      });

      // Populate equity watchlist filter dropdown
      const equityWatchlistFilter = $("equity-watchlist-filter");
      equityWatchlistFilter.innerHTML = '<option value="">All Symbols</option>';
      (watchlists.equity || []).forEach(sym => {
        const opt = document.createElement("option");
        opt.value = sym;
        opt.textContent = sym;
        equityWatchlistFilter.appendChild(opt);
      });

      // Populate commodity symbol select
      const commoditySelect = $("commodity-symbol-select");
      commoditySelect.innerHTML = '<option value="">Select Commodity Symbol</option>';
      (watchlists.commodity || []).forEach(sym => {
        const opt = document.createElement("option");
        opt.value = sym;
        opt.textContent = sym;
        commoditySelect.appendChild(opt);
      });

      // Populate index symbol select
      const indexSelect = $("index-symbol-select");
      indexSelect.innerHTML = '<option value="">Select Index Symbol</option>';
      (watchlists.index || []).forEach(sym => {
        const opt = document.createElement("option");
        opt.value = sym;
        opt.textContent = sym;
        indexSelect.appendChild(opt);
      });
    }

    // Run Scan handlers for each tab
    function setupScanHandler(tabId, selectId, buttonId, resultId) {
      const select = $(selectId);
      const button = $(buttonId);
      const result = $(resultId);

      button.addEventListener("click", async () => {
        const symbol = select.value;
        if (!symbol) {
          result.className = "scan-result show error";
          result.innerHTML = "Please select a symbol first";
          return;
        }
        button.textContent = "Scanning...";
        button.disabled = true;
        result.className = "scan-result show";
        result.innerHTML = "Scanning " + symbol + "...";
        try {
          const res = await fetch("/scan-symbol", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol })
          });
          const data = await res.json();
          if (data.error) {
            result.className = "scan-result show error";
            result.innerHTML = "Error: " + data.error;
          } else {
            result.className = "scan-result show success";
            const signalCount = data.signals || 0;
            result.innerHTML = `<strong>Scan Complete: ${signalCount} signals found for ${symbol}</strong>`;
            if (signalCount > 0) {
              // Get latest signals and show details
              fetch("/signals").then(r => r.json()).then(allSignals => {
                const symSignals = allSignals.filter(s => s.symbol === symbol).slice(-3);
                if (symSignals.length > 0) {
                  let detailsHtml = '<div class="signal-details">';
                  symSignals.forEach(sig => {
                    detailsHtml += `<div class="signal-row">
                      <span class="signal-label">${sig.direction.toUpperCase()} @ ${fmt.format(sig.entry)}</span>
                      <span class="signal-value">SL: ${fmt.format(sig.stop_loss)} | TGT: ${fmt.format(sig.target)}</span>
                    </div>`;
                  });
                  detailsHtml += '</div>';
                  result.innerHTML += detailsHtml;
                }
              });
            }
          }
          loadDashboard();
        } catch (e) {
          result.className = "scan-result show error";
          result.innerHTML = "Scan failed: " + e.message;
        } finally {
          button.textContent = "Run Scan";
          button.disabled = false;
        }
      });
    }

    setupScanHandler("tab-equity", "equity-symbol-select", "equity-scan", "equity-scan-result");
    setupScanHandler("tab-commodity", "commodity-symbol-select", "commodity-scan", "commodity-scan-result");
    setupScanHandler("tab-index", "index-symbol-select", "index-scan", "index-scan-result");

    function renderSignals(signals, targetId, section) {
      const filterBadge = section ? renderFilterBadge(section) : '';
      if (!signals.length) {
        $(targetId).innerHTML = filterBadge + `<div class="empty">No signals recorded yet. The swing alert agent will populate this after scans.</div>`;
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
      $(targetId).innerHTML = filterBadge + `<table><thead><tr><th>Symbol</th><th>Side</th><th>Score</th><th>Entry</th><th>Target</th></tr></thead><tbody>${rows}</tbody></table>`;
    }

    function renderAlerts(alerts, targetId, section) {
      const filterBadge = section ? renderFilterBadge(section) : '';
      if (!alerts.length) {
        $(targetId).innerHTML = filterBadge + `<div class="empty">No swing alerts yet.</div>`;
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
      $(targetId).innerHTML = filterBadge + `<table><thead><tr><th>Symbol</th><th>Setup</th><th>Score</th><th>Price</th><th>Message</th></tr></thead><tbody>${rows}</tbody></table>`;
    }

    // Filter state for each section
    const filters = { equity: null, commodity: null, index: null, alerts: null };

    function renderWatchlist(symbols, targetId, section) {
      if (!symbols.length) {
        $(targetId).innerHTML = `<div class="empty">No symbols configured.</div>`;
        return;
      }
      const currentFilter = filters[section];
      $(targetId).innerHTML = symbols.map((symbol, index) => `
        <div class="symbol-row ${currentFilter === symbol ? 'active-filter' : ''}" onclick="filterBySymbol(&quot;${section}&quot;, &quot;${escapeHtml(symbol)}&quot;)" style="cursor:pointer">
          <span>${index + 1}</span><strong>${escapeHtml(symbol)}</strong>
          ${currentFilter === symbol ? '<span class="filter-clear" onclick="event.stopPropagation(); clearFilter(&quot;' + section + '&quot;)">✕</span>' : ''}
        </div>
      `).join("");
    }

    function filterBySymbol(section, symbol) {
      if (filters[section] === symbol) {
        clearFilter(section);
      } else {
        filters[section] = symbol;
        loadDashboard();
      }
    }

    function filterEquityBySymbol(symbol) {
      filters.equity = symbol || null;
      loadDashboard();
    }

    function clearFilter(section) {
      filters[section] = null;
      loadDashboard();
    }

    function filterAlertsBySegment(segment) {
      filters.alerts = segment || null;
      loadDashboard();
    }

    function getFilteredSignals(allSignals, section) {
      const filter = filters[section];
      if (!filter) return allSignals;
      return allSignals.filter(s => s.symbol === filter);
    }

    function getFilteredAlerts(allAlerts, section) {
      const filter = filters[section];
      if (!filter) return allAlerts;
      return allAlerts.filter(a => a.symbol === filter);
    }

    function renderFilterBadge(section) {
      const filter = filters[section];
      if (!filter) return '';
      return `<div class="filter-badge">Filtered: ${escapeHtml(filter)} <span class="clear" onclick="clearFilter(&quot;${section}&quot;)">✕</span></div>`;
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
