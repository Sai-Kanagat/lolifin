"""
LoliFin — Streamlit dashboard.

Editorial Terminal palette (warm cream paper, ink-black, coral accent)
applied to the dashboard structure that worked: live agent progress at top,
KPI tiles with 'why?' expanders below them, charts row, two-column body,
deep-dive tabs, pipeline log + footer at bottom.

Run: streamlit run app.py
"""
import base64
import time
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from graph import graph

st.set_page_config(
    page_title="LoliFin · Equity Research",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── Load logo ────────────────────────────────────────────────────────────
def _load_logo() -> str:
    p = Path(__file__).parent / "assets" / "logo.svg"
    if p.exists():
        b = base64.b64encode(p.read_bytes()).decode()
        return f"data:image/svg+xml;base64,{b}"
    return ""


LOGO_URI = _load_logo()


# ── Design system CSS (ONE st.markdown call, ONE <style> block) ──────────
st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
  --paper: #F2E8DA;
  --paper-dim: #EADFCE;
  --paper-deep: #E0D2BC;
  --paper-card: #FBF6EE;
  --salmon: #F4C9A8;
  --ink: #1A1714;
  --ink-2: #5C544A;
  --ink-3: #8A8175;
  --rule: rgba(26,23,20,0.15);
  --rule-strong: rgba(26,23,20,0.30);
  --coral: #FF5B3C;
  --coral-soft: #FFDFD4;
  --bull: #1F7A4D;
  --bull-soft: #D4E7DC;
  --bear: #C2391C;
  --bear-soft: #F4D3C9;
  --terminal: #0E1410;
  --phosphor: #6FE39A;
  --serif: 'Instrument Serif', Georgia, serif;
  --sans: 'Geist', -apple-system, BlinkMacSystemFont, sans-serif;
  --mono: 'JetBrains Mono', ui-monospace, Menlo, monospace;
}

html, body, .stApp { background: #F2E8DA !important; }
.stApp { font-family: var(--sans); color: var(--ink); }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none; }
.main .block-container { padding-top: 0 !important; max-width: 1280px; }

.stApp p, .stApp li, .stApp span, .stApp div,
.stMarkdown, .stMarkdown p, .stMarkdown li { color: var(--ink); font-family: var(--sans); }
h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  color: var(--ink) !important; font-family: var(--sans); letter-spacing: -0.01em;
}

.masthead {
  margin: -1rem -1rem 24px -1rem; padding: 20px 32px;
  background: var(--paper); border-bottom: 1px solid var(--rule-strong);
  display: flex; align-items: center; justify-content: space-between;
}
.masthead img { height: 56px; display: block; }
.masthead-right {
  font-family: var(--sans); font-size: 13px; color: var(--ink);
  text-align: right; line-height: 1.55;
  background: var(--paper-card); border: 1px solid var(--rule-strong);
  border-radius: 4px; padding: 10px 14px;
}
.masthead-right b { color: var(--ink); font-weight: 700; }
.masthead-right .credit-meta {
  color: var(--ink-2); font-size: 11px; margin-top: 2px;
  text-transform: uppercase; letter-spacing: 0.06em; font-weight: 500;
}
.tagline {
  font-family: var(--sans); font-size: 11px; color: var(--ink-2);
  text-transform: uppercase; letter-spacing: 0.14em; font-weight: 600;
  margin-top: 4px;
}

.section {
  font-family: var(--sans); font-size: 11px; font-weight: 700;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-2);
  margin: 28px 0 10px 0; padding-bottom: 6px;
  border-bottom: 1px solid var(--rule);
}

.tile {
  background: var(--paper-card); border: 1px solid var(--rule-strong);
  padding: 14px 16px; min-height: 92px; border-radius: 4px;
}
.tile-label {
  font-family: var(--sans); font-size: 10px; color: var(--ink-2);
  text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700;
  margin-bottom: 6px;
}
.tile-value {
  font-family: var(--mono); font-size: 24px; color: var(--ink);
  font-weight: 500; font-feature-settings: 'tnum' 1; line-height: 1.1;
  letter-spacing: -0.01em;
}
.tile-value.bull { color: var(--bull); }
.tile-value.bear { color: var(--bear); }
.tile-sub {
  font-family: var(--mono); font-size: 11px; color: var(--ink-3);
  margin-top: 4px; font-feature-settings: 'tnum' 1;
}

.memo-hero {
  margin: 16px 0 4px 0; padding: 18px 0;
  border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule);
  display: flex; justify-content: space-between; align-items: flex-start;
}
.memo-company {
  font-family: var(--serif); font-size: 44px; line-height: 1.05;
  color: var(--ink); letter-spacing: -0.02em; font-weight: 400;
}
.memo-ticker {
  font-family: var(--mono); font-size: 13px; color: var(--ink-2);
  font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
  margin-top: 6px;
}
.memo-meta {
  font-family: var(--sans); font-size: 13px; color: var(--ink-3); margin-top: 2px;
}

.rec-badge {
  font-family: var(--mono); font-weight: 700; font-size: 17px;
  padding: 9px 16px; letter-spacing: 0.05em; border: 1.5px solid;
  display: inline-block; border-radius: 4px;
}
.rec-BUY  { color: var(--bull); border-color: var(--bull);  background: var(--bull-soft); }
.rec-HOLD { color: var(--ink);  border-color: var(--ink);   background: var(--paper-card); }
.rec-SELL { color: var(--bear); border-color: var(--bear);  background: var(--bear-soft); }

.body { font-family: var(--sans); font-size: 14.5px; line-height: 1.65; color: var(--ink); }
.body p, .body li, .body strong, .body b { color: var(--ink); }

.pull-quote {
  font-family: var(--serif); font-size: 18px; line-height: 1.5;
  color: var(--ink); padding: 8px 0 8px 18px;
  border-left: 3px solid var(--coral); max-width: 680px;
  font-style: italic;
}

.risk-pill {
  font-family: var(--mono); font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.08em;
  padding: 3px 8px; margin-right: 10px; display: inline-block; border: 1px solid;
}
.risk-high   { color: var(--bear); border-color: var(--bear); background: var(--bear-soft); }
.risk-medium { color: var(--ink-2); border-color: var(--ink-2); background: var(--paper-dim); }
.risk-low    { color: var(--bull); border-color: var(--bull); background: var(--bull-soft); }
.risk-card {
  background: var(--paper-card); border: 1px solid var(--rule);
  padding: 12px 14px; margin-bottom: 8px; border-radius: 4px;
}
.risk-text { color: var(--ink); font-size: 14px; }
.risk-source {
  color: var(--ink-3); font-family: var(--mono); font-size: 10px;
  margin-top: 6px; text-transform: uppercase; letter-spacing: 0.06em;
}

.sent {
  font-family: var(--mono); font-size: 11px; font-weight: 700;
  padding: 4px 10px; text-transform: uppercase; letter-spacing: 0.08em;
  display: inline-block; border: 1px solid; border-radius: 4px;
}
.sent-positive { color: var(--bull); border-color: var(--bull); background: var(--bull-soft); }
.sent-neutral  { color: var(--ink-2); border-color: var(--rule-strong); background: var(--paper-card); }
.sent-negative { color: var(--bear); border-color: var(--bear); background: var(--bear-soft); }

/* Whole news card is a clickable anchor */
a.news-card {
  display: block; text-decoration: none !important;
  background: var(--paper-card); border: 1px solid var(--rule);
  border-left: 3px solid var(--coral); padding: 12px 14px; margin-bottom: 8px;
  border-radius: 4px; transition: all 150ms ease; color: var(--ink) !important;
}
a.news-card:hover {
  background: var(--paper-dim); border-left-color: var(--coral);
  transform: translateX(2px);
}
a.news-card .news-title {
  color: var(--ink) !important; font-size: 14px; font-weight: 500; line-height: 1.45;
}
.news-pub {
  color: var(--ink-3); font-family: var(--mono); font-size: 11px;
  margin-top: 6px; text-transform: uppercase; letter-spacing: 0.05em;
}
.news-cta {
  color: var(--coral); font-family: var(--mono); font-size: 10px;
  margin-top: 4px; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700;
}

/* Terminal panel for agent activity */
.terminal-pane {
  background: #0E1410; border: 1px solid #1F2A22;
  padding: 16px 20px; font-family: var(--mono); font-size: 13.5px;
  color: #9FF0BC; border-radius: 4px;
}
.terminal-pane * { color: #9FF0BC; }
.agent-row {
  display: flex; align-items: center; padding: 9px 0;
  border-bottom: 1px dashed rgba(159,240,188,0.18);
}
.agent-row:last-child { border-bottom: none; }
.agent-status { width: 24px; font-size: 14px; color: #FF5B3C !important; }
.agent-name {
  color: #FFFFFF !important; font-weight: 700; width: 120px;
  text-transform: uppercase; letter-spacing: 0.08em;
}
.agent-desc { color: #B8E8C8 !important; flex: 1; padding-right: 12px; }
.agent-time { color: #7FCFA0 !important; min-width: 60px; text-align: right; font-weight: 500; }
@keyframes blink-soft { 0%,100% { opacity: 0.5; } 50% { opacity: 1; } }
.agent-running .agent-status { animation: blink-soft 800ms ease-in-out infinite; }

/* Progress bar in coral */
.stProgress > div > div { background: var(--coral) !important; }
.stProgress > div { background: var(--paper-dim) !important; }

/* Inputs */
.stTextInput input {
  background: var(--paper-card) !important; color: var(--ink) !important;
  border: 1px solid var(--rule-strong) !important; border-radius: 4px !important;
  padding: 0.65rem 0.9rem !important; font-family: var(--mono) !important;
  font-size: 14px !important; font-weight: 500;
  text-transform: uppercase; letter-spacing: 0.05em;
}
.stTextInput input:focus {
  border-color: var(--coral) !important; box-shadow: 0 0 0 1px var(--coral) !important;
}

/* Buttons */
.stButton>button, .stButton>button p, .stButton>button span,
.stButton>button div {
  background: var(--ink) !important;
  color: #FBF6EE !important;
  border: 1px solid var(--ink) !important;
  font-family: var(--sans) !important;
  font-weight: 600 !important;
}
.stButton>button {
  border-radius: 4px !important;
  padding: 0.65rem 1.4rem !important;
  font-size: 14px !important;
  letter-spacing: 0.02em !important;
  transition: all 120ms ease;
  height: auto !important;
}
.stButton>button:hover, .stButton>button:hover p,
.stButton>button:hover span, .stButton>button:hover div {
  background: var(--coral) !important;
  border-color: var(--coral) !important;
  color: #FBF6EE !important;
  transform: translateY(-1px);
}

/* Expanders */
div[data-testid="stExpander"] {
  background: var(--paper-card); border: 1px solid var(--rule);
  border-radius: 4px; margin: 6px 0;
}
/* Only style the text — leave the chevron icon's font alone */
div[data-testid="stExpander"] summary p,
div[data-testid="stExpander"] summary span:not([data-testid*="Icon"]):not([class*="icon"]) {
  color: var(--ink) !important; font-family: var(--sans) !important;
  font-size: 13px !important; font-weight: 500 !important;
}
/* Hide the raw-text material icon names if they leak through */
div[data-testid="stExpander"] [data-testid="stExpanderToggleIcon"] {
  font-family: 'Material Symbols Rounded', 'Material Icons' !important;
  color: var(--ink-2) !important;
}
div[data-testid="stExpander"] details summary:hover { background: var(--paper-dim); }

.detail-card {
  background: var(--paper); border: 1px solid var(--rule);
  padding: 10px 12px; margin: 6px 0; border-radius: 4px;
}
.detail-label {
  color: var(--ink-2); font-size: 10px; text-transform: uppercase;
  letter-spacing: 0.1em; font-weight: 600;
}
.detail-value {
  color: var(--ink); font-family: var(--mono); font-size: 14px;
  font-weight: 500; margin-top: 2px; font-feature-settings: 'tnum' 1;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid var(--rule); }
.stTabs [data-baseweb="tab"] {
  background: transparent !important; color: var(--ink-2) !important;
  font-family: var(--sans) !important; font-size: 13px !important;
  font-weight: 500 !important; padding: 10px 16px !important;
  border: none !important; border-bottom: 2px solid transparent !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
  color: var(--ink) !important; border-bottom-color: var(--coral) !important;
}

/* Empty state */
.empty {
  background: var(--paper-card); border: 1px solid var(--rule);
  padding: 56px 40px; text-align: center; margin: 24px 0; border-radius: 4px;
}
.empty-title {
  font-family: var(--serif); font-size: 30px; color: var(--ink);
  line-height: 1.2; margin-bottom: 12px;
}
.empty-body {
  font-family: var(--sans); font-size: 14.5px; color: var(--ink-2);
  max-width: 520px; margin: 0 auto; line-height: 1.6;
}
.empty-tickers {
  font-family: var(--mono); margin-top: 14px; color: var(--ink);
  font-weight: 700; letter-spacing: 0.04em;
}

.chart-frame {
  background: var(--paper-card); border: 1px solid var(--rule);
  padding: 14px 16px; border-radius: 4px; margin-bottom: 8px;
}
.chart-label {
  font-family: var(--sans); font-size: 10px; color: var(--ink-2);
  text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700;
  margin-bottom: 10px;
}

/* Footer */
.footer {
  margin-top: 48px; padding: 24px 0 16px 0;
  border-top: 1px solid var(--rule-strong); color: var(--ink-2);
}
.footer-grid {
  display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 32px; margin-bottom: 20px;
}
.footer h4 {
  color: var(--ink) !important; font-family: var(--sans); font-size: 11px;
  text-transform: uppercase; letter-spacing: 0.14em; font-weight: 700; margin-bottom: 8px;
}
.footer-text { color: var(--ink-2); font-size: 13px; line-height: 1.7; }
.footer-bottom {
  text-align: center; padding-top: 16px; border-top: 1px solid var(--rule);
  color: var(--ink-3); font-family: var(--mono); font-size: 11px;
  letter-spacing: 0.05em;
}
</style>""",
    unsafe_allow_html=True,
)

# ── Session state ────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None

# ── Masthead ────────────────────────────────────────────────────────────
logo_html = (
    f'<img src="{LOGO_URI}" alt="LoliFin">' if LOGO_URI
    else '<span style="font-family:var(--serif);font-size:32px;">LoliFin</span>'
)
st.markdown(
    f"""
    <div class="masthead">
        <div>
            {logo_html}
            <div class="tagline">Agentic equity research</div>
        </div>
        <div class="masthead-right">
            A project by <b>Iolanda Costa</b>
            <div class="credit-meta">M.Sc. Finance &amp; AI · Bologna Business School</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Input row ────────────────────────────────────────────────────────────
col_in, col_btn = st.columns([5, 1])
with col_in:
    ticker = st.text_input(
        "Ticker", value="NVDA", label_visibility="collapsed",
        placeholder="Enter a ticker (e.g. NVDA, AAPL, MSFT)",
    ).upper().strip()
with col_btn:
    run = st.button("Generate memo", type="primary", use_container_width=True)


# ── Helpers ──────────────────────────────────────────────────────────────
def fmt_money(v):
    if v is None or not isinstance(v, (int, float)):
        return "—"
    if abs(v) >= 1_000_000: return f"${v/1_000_000:.2f}T"
    if abs(v) >= 1000:      return f"${v/1000:.2f}B"
    return f"${v:,.0f}M"


def fmt_pct(v, signed=False):
    if v is None or not isinstance(v, (int, float)): return "—"
    pct = v * 100 if abs(v) < 5 else v
    s = f"{pct:+.1f}%" if signed else f"{pct:.1f}%"
    return s.replace("-", "−")


def tile(label, value, sub="", value_class=""):
    sub_html = f'<div class="tile-sub">{sub}</div>' if sub else ""
    cls = f"tile-value {value_class}".strip()
    return (
        f'<div class="tile"><div class="tile-label">{label}</div>'
        f'<div class="{cls}">{value}</div>{sub_html}</div>'
    )


def risk_label(score):
    if score is None: return "—"
    if score <= 3: return "low risk"
    if score <= 6: return "moderate"
    return "elevated"


# Altair chart helper — consistent paper theme + interactivity + padding
def paper_chart(chart):
    return (
        chart
        .configure_view(strokeWidth=0, fill="#FBF6EE")
        .configure_axis(
            labelFont="JetBrains Mono", titleFont="Geist",
            labelColor="#5C544A", titleColor="#1A1714", labelFontSize=11,
            labelPadding=6, gridColor="rgba(26,23,20,0.08)",
            domainColor="#1A1714", tickColor="#5C544A",
        )
        .configure_legend(
            labelFont="Geist", labelColor="#1A1714", titleColor="#1A1714",
        )
        .properties(padding={"left": 14, "right": 14, "top": 8, "bottom": 8})
    )


# ── Agents ───────────────────────────────────────────────────────────────
AGENTS = [
    ("filings",   "Filings",   "Pulling fundamentals from Yahoo Finance"),
    ("news",      "News",      "Scanning recent headlines"),
    ("valuation", "Valuation", "Running DCF + comparable multiples"),
    ("risk",      "Risk",      "Cross-referencing red flags"),
    ("editor",    "Editor",    "Composing the memo"),
]
AGENT_KEYS = [a[0] for a in AGENTS]


def render_progress(container, statuses, timings):
    rows = []
    for key, name, desc in AGENTS:
        s = statuses.get(key, "pending")
        if s == "done":    icon, row_cls = "●", ""
        elif s == "running": icon, row_cls = "◐", "agent-running"
        else:              icon, row_cls = "○", ""
        current_desc = "complete" if s == "done" else desc
        t = timings.get(key, "")
        t_html = f'<span class="agent-time">{t}</span>' if t else ""
        rows.append(
            f'<div class="agent-row {row_cls}">'
            f'<span class="agent-status">{icon}</span>'
            f'<span class="agent-name">{name}</span>'
            f'<span class="agent-desc">{current_desc}</span>'
            f'{t_html}</div>'
        )
    container.markdown(
        f'<div class="terminal-pane">{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


# ── Run pipeline ─────────────────────────────────────────────────────────
if run:
    if not ticker:
        st.error("Enter a ticker.")
        st.stop()

    st.markdown('<div class="section">Pipeline · live</div>', unsafe_allow_html=True)
    progress_bar = st.progress(0, text="Initializing 5-agent pipeline")
    progress_box = st.empty()

    statuses, timings = {}, {}
    statuses[AGENT_KEYS[0]] = "running"
    render_progress(progress_box, statuses, timings)

    result = {}
    pipeline_start = time.time()
    completed = 0
    total = len(AGENT_KEYS)

    try:
        for event in graph.stream({"ticker": ticker}, stream_mode="updates"):
            for node_name, node_output in event.items():
                if node_name in AGENT_KEYS:
                    elapsed = time.time() - pipeline_start
                    statuses[node_name] = "done"
                    timings[node_name] = f"{elapsed:.1f}s"
                    completed += 1
                    pct = int((completed / total) * 100)
                    progress_bar.progress(pct, text=f"{completed} of {total} agents complete · {elapsed:.1f}s")
                    next_idx = AGENT_KEYS.index(node_name) + 1
                    if next_idx < total and statuses.get(AGENT_KEYS[next_idx]) is None:
                        statuses[AGENT_KEYS[next_idx]] = "running"
                    render_progress(progress_box, statuses, timings)
                if isinstance(node_output, dict):
                    for k, v in node_output.items():
                        if k == "errors":
                            result.setdefault("errors", []).extend(v or [])
                        else:
                            result[k] = v

        for k in AGENT_KEYS:
            if statuses.get(k) != "done":
                statuses[k] = "done"
        total_time = time.time() - pipeline_start
        progress_bar.progress(100, text=f"Complete · {total_time:.1f}s total")
        render_progress(progress_box, statuses, timings)
        time.sleep(0.4)
        progress_bar.empty()
        progress_box.empty()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        st.stop()

    result["ticker"] = ticker
    result["_timings"] = timings
    result["_total_time"] = total_time
    st.session_state.result = result


# ── Render results ──────────────────────────────────────────────────────
result = st.session_state.result

if result:
    ticker = result.get("ticker", "")
    company = result.get("company_name") or ticker
    rec = result.get("recommendation") or "HOLD"
    val = result.get("valuation") or {}
    fins = result.get("financials") or {}
    risks = result.get("risks") or []
    risk_score = result.get("risk_score")
    sentiment = (result.get("news_sentiment") or "neutral").lower()
    price_history = result.get("price_history") or []
    upside = val.get("upside_pct")

    # ── Hero ────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="memo-hero">
            <div>
                <div class="memo-company">{company}</div>
                <div class="memo-ticker">{ticker}</div>
                <div class="memo-meta">
                    {fins.get('sector') or ''}
                    {' · ' + fins.get('industry') if fins.get('industry') else ''}
                </div>
            </div>
            <div><span class="rec-badge rec-{rec}">{rec}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI tiles ──────────────────────────────────────────────
    upside_class = "bull" if (isinstance(upside, (int, float)) and upside > 0) else (
        "bear" if (isinstance(upside, (int, float)) and upside < 0) else ""
    )
    upside_str = fmt_pct(upside, signed=True) if upside is not None else "—"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(tile("Current price",
                         f"${val.get('current_price'):.2f}" if val.get('current_price') else "—"),
                    unsafe_allow_html=True)
    with c2:
        fv = val.get("blended_fair_value")
        dcf = val.get("dcf_fair_value"); comp = val.get("comp_fair_value")
        sub = ""
        if dcf and comp: sub = f"DCF ${dcf} · Comps ${comp}"
        elif dcf: sub = f"DCF ${dcf}"
        elif comp: sub = f"Comps ${comp}"
        st.markdown(tile("Fair value", f"${fv:.2f}" if fv else "—", sub),
                    unsafe_allow_html=True)
    with c3:
        st.markdown(tile("Upside", upside_str, "vs current price", value_class=upside_class),
                    unsafe_allow_html=True)
    with c4:
        rs_display = f"{risk_score}/10" if risk_score else "—"
        st.markdown(tile("Risk score", rs_display, risk_label(risk_score)),
                    unsafe_allow_html=True)

    # KPI "why?" expanders (separate row → no overlap with tiles above)
    e1, e2, e3, e4 = st.columns(4)
    with e1:
        with st.expander("Why this price?"):
            mc = fmt_money(fins.get('market_cap'))
            pe = f"{fins.get('trailing_pe'):.1f}x" if fins.get('trailing_pe') else "—"
            st.markdown(
                f"<div class='body'>Live mid-quote from Yahoo Finance.<br/>"
                f"<b>Market cap:</b> {mc}<br/><b>Trailing P/E:</b> {pe}</div>",
                unsafe_allow_html=True,
            )
    with e2:
        with st.expander("How was fair value calculated?"):
            a = val.get("assumptions") or {}
            st.markdown(
                f"<div class='body'><b>DCF assumptions</b><br/>"
                f"WACC: {fmt_pct(a.get('wacc'))}<br/>"
                f"Growth: {fmt_pct(a.get('growth'))}<br/>"
                f"Terminal multiple: {a.get('terminal_multiple') or '—'}x<br/>"
                f"Sector P/E (for comps): {a.get('sector_pe') or '—'}<br/><br/>"
                f"<b>Blended</b> = average of DCF and Comps methods.</div>",
                unsafe_allow_html=True,
            )
    with e3:
        with st.expander("What does this mean?"):
            if isinstance(upside, (int, float)):
                direction = "above" if upside > 0 else "below"
                st.markdown(
                    f"<div class='body'>Blended fair value is "
                    f"<b>{abs(upside):.1f}% {direction}</b> current price.<br/><br/>"
                    f"<b>Thresholds</b><br/>"
                    f"BUY if upside &gt; 15% AND risk ≤ 5<br/>"
                    f"SELL if upside &lt; −10% OR risk ≥ 8<br/>"
                    f"Else HOLD</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("<div class='body'>Upside unavailable.</div>", unsafe_allow_html=True)
    with e4:
        with st.expander("Why this risk score?"):
            if risks:
                sc = {"high": 0, "medium": 0, "low": 0}
                for r in risks:
                    sev = (r.get("severity") or "medium").lower()
                    if sev in sc: sc[sev] += 1
                st.markdown(
                    f"<div class='body'>{len(risks)} risks identified.<br/>"
                    f"<span style='color:var(--bear);'><b>{sc['high']} high</b></span> · "
                    f"<b>{sc['medium']} medium</b> · "
                    f"<span style='color:var(--bull);'><b>{sc['low']} low</b></span><br/><br/>"
                    f"Score (1 safe → 10 avoid) blends count, severity mix, and source "
                    f"diversity across filings, news, and valuation signals.</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("<div class='body'>No risks identified.</div>", unsafe_allow_html=True)

    # ── Charts row 1: Price + Valuation ────────────────────────
    st.markdown('<div class="section">Visuals</div>', unsafe_allow_html=True)
    chart_left, chart_right = st.columns([1.4, 1])

    with chart_left:
        st.markdown('<div class="chart-label">6-month price history</div>', unsafe_allow_html=True)
        if price_history:
            df = pd.DataFrame(price_history)
            df["date"] = pd.to_datetime(df["date"])
            try:
                line = (
                    alt.Chart(df)
                    .mark_line(color="#FF5B3C", strokeWidth=2)
                    .encode(
                        x=alt.X("date:T", title=None),
                        y=alt.Y("close:Q", title=None, scale=alt.Scale(zero=False)),
                        tooltip=[alt.Tooltip("date:T", title="Date"),
                                 alt.Tooltip("close:Q", title="Close", format="$.2f")],
                    )
                    .properties(height=260)
                    .interactive()
                )
                st.altair_chart(paper_chart(line), use_container_width=True)
            except Exception:
                st.line_chart(df.set_index("date")["close"], height=260)
        else:
            st.markdown("<div class='body'>Price history unavailable.</div>", unsafe_allow_html=True)

    with chart_right:
        st.markdown('<div class="chart-label">Valuation comparison</div>', unsafe_allow_html=True)
        bars = []
        if val.get("current_price"): bars.append({"method": "Current", "value": val["current_price"]})
        if val.get("dcf_fair_value"): bars.append({"method": "DCF", "value": val["dcf_fair_value"]})
        if val.get("comp_fair_value"): bars.append({"method": "Comps", "value": val["comp_fair_value"]})
        if val.get("blended_fair_value"): bars.append({"method": "Blended", "value": val["blended_fair_value"]})
        if bars:
            bdf = pd.DataFrame(bars)
            try:
                bar = (
                    alt.Chart(bdf)
                    .mark_bar(size=36)
                    .encode(
                        x=alt.X("method:N", title=None, sort=None,
                                axis=alt.Axis(labelAngle=0, labelFont="JetBrains Mono")),
                        y=alt.Y("value:Q", title=None, axis=alt.Axis(format="$.0f")),
                        color=alt.Color("method:N", scale=alt.Scale(
                            domain=["Current", "DCF", "Comps", "Blended"],
                            range=["#5C544A", "#1F7A4D", "#F5C842", "#FF5B3C"],
                        ), legend=None),
                        tooltip=[alt.Tooltip("method"), alt.Tooltip("value:Q", format="$.2f")],
                    )
                    .properties(height=260)
                )
                st.altair_chart(paper_chart(bar), use_container_width=True)
            except Exception:
                st.bar_chart(bdf.set_index("method"))
        else:
            st.markdown("<div class='body'>Valuation data unavailable.</div>", unsafe_allow_html=True)

    # ── Charts row 2: margins, cash/debt, risk donut ───────────
    v1, v2, v3 = st.columns(3)

    with v1:
        st.markdown('<div class="chart-label">Margins</div>', unsafe_allow_html=True)
        m_data = []
        if fins.get("gross_margin") is not None:
            m_data.append({"type": "Gross", "value": fins["gross_margin"] * 100})
        if fins.get("operating_margin") is not None:
            m_data.append({"type": "Operating", "value": fins["operating_margin"] * 100})
        if m_data:
            mdf = pd.DataFrame(m_data)
            try:
                mc = (
                    alt.Chart(mdf)
                    .mark_bar(size=28)
                    .encode(
                        y=alt.Y("type:N", title=None, sort=None,
                                axis=alt.Axis(labelFont="Geist", labelFontSize=12)),
                        x=alt.X("value:Q", title=None, scale=alt.Scale(domain=[0, 100]),
                                axis=alt.Axis(format=".0f")),
                        color=alt.value("#1F7A4D"),
                        tooltip=[alt.Tooltip("type"), alt.Tooltip("value:Q", format=".1f", title="%")],
                    )
                    .properties(height=200)
                )
                st.altair_chart(paper_chart(mc), use_container_width=True)
            except Exception:
                st.bar_chart(mdf.set_index("type"))
        else:
            st.markdown("<div class='body'>Margin data unavailable.</div>", unsafe_allow_html=True)

    with v2:
        st.markdown('<div class="chart-label">Cash vs debt</div>', unsafe_allow_html=True)
        cd_data = []
        if fins.get("cash") is not None: cd_data.append({"type": "Cash", "value": fins["cash"]})
        if fins.get("total_debt") is not None: cd_data.append({"type": "Debt", "value": fins["total_debt"]})
        if cd_data:
            cdf = pd.DataFrame(cd_data)
            try:
                cc = (
                    alt.Chart(cdf)
                    .mark_bar(size=42)
                    .encode(
                        x=alt.X("type:N", title=None, sort=None,
                                axis=alt.Axis(labelAngle=0, labelFont="Geist")),
                        y=alt.Y("value:Q", title=None, axis=alt.Axis(format="$,.0f")),
                        color=alt.Color("type:N", scale=alt.Scale(
                            domain=["Cash", "Debt"], range=["#1F7A4D", "#C2391C"]), legend=None),
                        tooltip=[alt.Tooltip("type"),
                                 alt.Tooltip("value:Q", format="$,.0f", title="$M")],
                    )
                    .properties(height=200)
                )
                st.altair_chart(paper_chart(cc), use_container_width=True)
            except Exception:
                st.bar_chart(cdf.set_index("type"))
        else:
            st.markdown("<div class='body'>Balance sheet data unavailable.</div>", unsafe_allow_html=True)

    with v3:
        st.markdown('<div class="chart-label">Risk severity mix</div>', unsafe_allow_html=True)
        if risks:
            sc = {"high": 0, "medium": 0, "low": 0}
            for r in risks:
                sev = (r.get("severity") or "medium").lower()
                if sev in sc: sc[sev] += 1
            rdf = pd.DataFrame([{"severity": k, "count": v} for k, v in sc.items() if v > 0])
            if not rdf.empty:
                try:
                    donut = (
                        alt.Chart(rdf)
                        .mark_arc(innerRadius=38, outerRadius=70,
                                  stroke="#FBF6EE", strokeWidth=2)
                        .encode(
                            theta=alt.Theta("count:Q"),
                            color=alt.Color("severity:N", scale=alt.Scale(
                                domain=["high", "medium", "low"],
                                range=["#C2391C", "#5C544A", "#1F7A4D"],
                            ), legend=alt.Legend(
                                orient="bottom", labelColor="#1A1714",
                                title=None, labelFont="Geist", labelFontSize=11,
                            )),
                            tooltip=["severity", "count"],
                        )
                        .properties(height=240)
                    )
                    st.altair_chart(paper_chart(donut), use_container_width=True)
                except Exception:
                    st.bar_chart(rdf.set_index("severity"))
        else:
            st.markdown("<div class='body'>No risks to chart.</div>", unsafe_allow_html=True)

    # ── Two-column body ─────────────────────────────────────────
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown('<div class="section">Fundamentals</div>', unsafe_allow_html=True)
        f1, f2 = st.columns(2)
        with f1:
            st.markdown(tile("Revenue (TTM)", fmt_money(fins.get("revenue_ttm"))), unsafe_allow_html=True)
            st.markdown("")
            st.markdown(tile("Free cash flow", fmt_money(fins.get("free_cash_flow_ttm"))), unsafe_allow_html=True)
            st.markdown("")
            st.markdown(tile("Operating margin", fmt_pct(fins.get("operating_margin"))), unsafe_allow_html=True)
        with f2:
            st.markdown(tile("Net income (TTM)", fmt_money(fins.get("net_income_ttm"))), unsafe_allow_html=True)
            st.markdown("")
            st.markdown(tile("Total debt", fmt_money(fins.get("total_debt"))), unsafe_allow_html=True)
            st.markdown("")
            g = fins.get("revenue_growth_yoy")
            g_cls = "bull" if (isinstance(g, (int, float)) and g > 0) else (
                "bear" if (isinstance(g, (int, float)) and g < 0) else ""
            )
            st.markdown(tile("Revenue growth (YoY)",
                             fmt_pct(g, signed=True) if g else "—", value_class=g_cls),
                        unsafe_allow_html=True)

        with st.expander("More fundamentals"):
            pe_block = (
                f"<div class='detail-card'><div class='detail-label'>Trailing P/E</div>"
                f"<div class='detail-value'>{fins.get('trailing_pe'):.1f}x</div></div>"
                if fins.get('trailing_pe') else
                f"<div class='detail-card'><div class='detail-label'>Trailing P/E</div>"
                f"<div class='detail-value'>—</div></div>"
            )
            st.markdown(
                f"<div class='detail-card'><div class='detail-label'>Market cap</div>"
                f"<div class='detail-value'>{fmt_money(fins.get('market_cap'))}</div></div>"
                f"<div class='detail-card'><div class='detail-label'>Gross margin</div>"
                f"<div class='detail-value'>{fmt_pct(fins.get('gross_margin'))}</div></div>"
                f"<div class='detail-card'><div class='detail-label'>Cash on hand</div>"
                f"<div class='detail-value'>{fmt_money(fins.get('cash'))}</div></div>"
                f"{pe_block}",
                unsafe_allow_html=True,
            )

        val_notes = (result.get("valuation_notes") or "").strip()
        if val_notes:
            st.markdown('<div class="section">Valuation commentary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="pull-quote">{val_notes}</div>', unsafe_allow_html=True)

        biz_summary = (fins.get("summary") or "").strip()
        if biz_summary:
            st.markdown('<div class="section">Business summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="body">{biz_summary}</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section">Key risks</div>', unsafe_allow_html=True)
        if risks:
            for r in risks[:6]:
                sev = (r.get("severity") or "medium").lower()
                if sev not in ("low", "medium", "high"): sev = "medium"
                st.markdown(
                    f'<div class="risk-card">'
                    f'<span class="risk-pill risk-{sev}">{sev}</span>'
                    f'<span class="risk-text">{r.get("risk", "")}</span>'
                    f'<div class="risk-source">Source · {r.get("source", "—")}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="body">No risks flagged.</div>', unsafe_allow_html=True)

        st.markdown('<div class="section">News &amp; sentiment</div>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="sent sent-{sentiment}">Sentiment · {sentiment}</span>',
            unsafe_allow_html=True,
        )
        news_sum = (result.get("news_summary") or "").strip()
        if news_sum:
            st.markdown(
                f'<div class="body" style="margin-top:10px;">{news_sum}</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div class='chart-label' style='margin-top:18px;'>Recent headlines</div>",
            unsafe_allow_html=True,
        )
        for s in (result.get("news_sources") or [])[:6]:
            title = s.get("title", "")
            url = s.get("url") or "#"
            pub = s.get("publisher") or ""
            st.markdown(
                f'<a class="news-card" href="{url}" target="_blank" rel="noopener">'
                f'<div class="news-title">{title}</div>'
                f'<div class="news-pub">{pub}</div>'
                f'<div class="news-cta">Read article →</div></a>',
                unsafe_allow_html=True,
            )

    # ── Deep dive ────────────────────────────────────────────────
    st.markdown('<div class="section">Deep dive</div>', unsafe_allow_html=True)
    if result.get("memo_markdown"):
        with st.expander("Full investment memo", expanded=False):
            st.markdown(f"<div class='body'>{result['memo_markdown']}</div>",
                        unsafe_allow_html=True)

    with st.expander("Agent outputs (structured view)"):
        tabs = st.tabs(["Filings", "News", "Valuation", "Risk", "Editor"])
        with tabs[0]:
            for k, v in (fins or {}).items():
                if v is None: continue
                disp = v
                if isinstance(v, float) and 0 < v < 1: disp = f"{v*100:.2f}%"
                elif isinstance(v, (int, float)): disp = f"{v:,.2f}"
                st.markdown(
                    f"<div class='detail-card'><div class='detail-label'>{k.replace('_', ' ').title()}</div>"
                    f"<div class='detail-value'>{disp}</div></div>",
                    unsafe_allow_html=True,
                )
        with tabs[1]:
            st.markdown(f"<div class='body'><b>Sentiment:</b> {sentiment}<br/><br/>"
                        f"{result.get('news_summary')}</div>", unsafe_allow_html=True)
            for s in (result.get("news_sources") or []):
                st.markdown(
                    f'<a class="news-card" href="{s.get("url") or "#"}" target="_blank" rel="noopener">'
                    f'<div class="news-title">{s.get("title", "")}</div>'
                    f'<div class="news-pub">{s.get("publisher") or ""}</div></a>',
                    unsafe_allow_html=True,
                )
        with tabs[2]:
            for k, v in (val or {}).items():
                if k == "assumptions":
                    st.markdown(
                        f"<div class='detail-card'><div class='detail-label'>Assumptions</div>"
                        f"<div class='detail-value' style='font-size:12.5px;'>"
                        f"{', '.join(f'{kk}: {vv}' for kk, vv in (v or {}).items() if vv is not None)}"
                        f"</div></div>", unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<div class='detail-card'><div class='detail-label'>{k.replace('_', ' ').title()}</div>"
                        f"<div class='detail-value'>{v}</div></div>",
                        unsafe_allow_html=True,
                    )
            st.markdown(f"<div class='body' style='margin-top:10px;'>{result.get('valuation_notes', '')}</div>",
                        unsafe_allow_html=True)
        with tabs[3]:
            for r in risks:
                sev = (r.get("severity") or "medium").lower()
                st.markdown(
                    f'<div class="risk-card">'
                    f'<span class="risk-pill risk-{sev}">{sev}</span>'
                    f'<span class="risk-text">{r.get("risk", "")}</span>'
                    f'<div class="risk-source">Source · {r.get("source", "—")}</div></div>',
                    unsafe_allow_html=True,
                )
        with tabs[4]:
            st.markdown(
                f"<div class='body'><b>Recommendation:</b> {rec}<br/><br/>"
                f"<b>Decision logic</b><br/>"
                f"BUY if upside &gt; 15% AND risk ≤ 5<br/>"
                f"SELL if upside &lt; −10% OR risk ≥ 8<br/>"
                f"Else HOLD</div>",
                unsafe_allow_html=True,
            )

    # ── Pipeline log (collapsed, at the bottom) ──────────────────
    timings = result.get("_timings") or {}
    total_t = result.get("_total_time") or 0
    with st.expander(f"Pipeline log · {total_t:.1f}s total"):
        rows = []
        for key, name, desc in AGENTS:
            t = timings.get(key, "—")
            rows.append(
                f'<div class="agent-row">'
                f'<span class="agent-status">●</span>'
                f'<span class="agent-name">{name}</span>'
                f'<span class="agent-desc">{desc}</span>'
                f'<span class="agent-time">{t}</span></div>'
            )
        st.markdown(f'<div class="terminal-pane">{"".join(rows)}</div>',
                    unsafe_allow_html=True)

    if result.get("errors"):
        with st.expander(f"Agent warnings · {len(result['errors'])}"):
            for e in result["errors"]:
                st.warning(e)

else:
    # ── Empty state ──────────────────────────────────────────────
    st.markdown(
        """
        <div class="empty">
            <div class="empty-title">Equity research, without the analyst hours.</div>
            <div class="empty-body">
                LoliFin reads the filings, models the business, and writes the memo —
                in about twenty seconds. Enter a ticker above to begin.
            </div>
            <div class="empty-tickers">NVDA  ·  AAPL  ·  MSFT  ·  TSLA</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Footer ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="footer">
        <div class="footer-grid">
            <div>
                <h4>About LoliFin</h4>
                <div class="footer-text">
                    A multi-agent AI system that produces equity research memos.
                    Built as part of a Master's in Finance &amp; AI portfolio at
                    Bologna Business School.
                </div>
            </div>
            <div>
                <h4>Pipeline</h4>
                <div class="footer-text">
                    1 Filings · fundamentals<br/>
                    2 News · sentiment<br/>
                    3 Valuation · DCF + comps<br/>
                    4 Risk · red flags<br/>
                    5 Editor · final memo
                </div>
            </div>
            <div>
                <h4>Stack</h4>
                <div class="footer-text">
                    Python · LangGraph<br/>
                    Gemini 2.5 Flash<br/>
                    yfinance · Yahoo News<br/>
                    Streamlit · Altair
                </div>
            </div>
        </div>
        <div class="footer-bottom">
            © 2026 Iolanda Costa · LoliFin · For educational purposes only — not investment advice.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
