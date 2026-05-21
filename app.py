"""
LoliFin — Streamlit dashboard.

Editorial Terminal aesthetic: warm cream paper, ink-black serifs,
JetBrains Mono numbers, coral accent. Per LoliFin design system.

Run: streamlit run app.py
"""
import time
import pandas as pd
import streamlit as st
import altair as alt

from graph import graph

st.set_page_config(
    page_title="LoliFin · Equity Research",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design system CSS ────────────────────────────────────────────────────
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
    :root {
      --paper:        #F2E8DA;
      --paper-dim:    #EADFCE;
      --paper-deep:   #E0D2BC;
      --paper-card:   #FBF6EE;
      --salmon:       #F4C9A8;
      --salmon-deep:  #E8B58E;
      --ink:          #1A1714;
      --ink-2:        #5C544A;
      --ink-3:        #8A8175;
      --rule:         rgba(26, 23, 20, 0.15);
      --rule-strong:  rgba(26, 23, 20, 0.30);
      --coral:        #FF5B3C;
      --coral-soft:   #FFDFD4;
      --bull:         #1F7A4D;
      --bull-soft:    #D4E7DC;
      --bear:         #C2391C;
      --bear-soft:    #F4D3C9;
      --highlight:    #F5C842;
      --terminal:     #0E1410;
      --terminal-2:   #161E18;
      --phosphor:     #6FE39A;
      --serif:   'Instrument Serif', Georgia, serif;
      --sans:    'Geist', -apple-system, BlinkMacSystemFont, sans-serif;
      --mono:    'JetBrains Mono', ui-monospace, Menlo, monospace;
    }

    /* Base */
    html, body, .stApp { background: var(--paper) !important; }
    .stApp { font-family: var(--sans); color: var(--ink); }
    #MainMenu, footer, header { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none; }

    /* Paper grain */
    .stApp::before {
        content: ""; position: fixed; inset: 0; pointer-events: none;
        background-image: radial-gradient(rgba(26,23,20,0.025) 1px, transparent 1px);
        background-size: 3px 3px; z-index: 0;
    }
    .main .block-container { position: relative; z-index: 1; padding-top: 0 !important; }

    /* Override Streamlit text */
    .stApp p, .stApp li, .stApp span, .stApp div,
    .stMarkdown, .stMarkdown p, .stMarkdown li {
        color: var(--ink); font-family: var(--sans);
    }
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--ink) !important; font-family: var(--sans);
        letter-spacing: -0.01em;
    }

    /* Masthead */
    .masthead {
        margin: -1rem -1rem 28px -1rem; padding: 16px 32px;
        background: var(--paper); border-bottom: 1px solid var(--rule-strong);
        display: flex; align-items: center; justify-content: space-between;
    }
    .masthead-left { display: flex; align-items: baseline; gap: 14px; }
    .wordmark {
        font-family: var(--serif); font-size: 32px; font-weight: 400;
        color: var(--ink); letter-spacing: -0.02em; line-height: 1;
    }
    .wordmark .accent { color: var(--coral); }
    .tagline {
        font-family: var(--sans); font-size: 12px; color: var(--ink-2);
        text-transform: uppercase; letter-spacing: 0.12em; font-weight: 500;
    }
    .masthead-right {
        font-family: var(--sans); font-size: 12px; color: var(--ink-2);
        text-align: right; line-height: 1.5;
    }
    .masthead-right b { color: var(--ink); font-weight: 600; }

    /* Hero memo header */
    .memo-hero {
        margin: 18px 0 8px 0; padding: 24px 0;
        border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule);
    }
    .memo-h-row { display: flex; align-items: flex-start; justify-content: space-between; }
    .memo-company {
        font-family: var(--serif); font-size: 48px; line-height: 1.05;
        color: var(--ink); letter-spacing: -0.02em; font-weight: 400;
    }
    .memo-ticker {
        font-family: var(--mono); font-size: 14px; color: var(--ink-2);
        font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;
        margin-top: 6px;
    }
    .memo-meta {
        font-family: var(--sans); font-size: 13px; color: var(--ink-3);
        margin-top: 4px;
    }

    /* Recommendation badge */
    .rec-badge {
        font-family: var(--mono); font-weight: 700; font-size: 18px;
        padding: 10px 18px; letter-spacing: 0.05em; border: 1.5px solid;
        display: inline-block;
    }
    .rec-BUY  { color: var(--bull); border-color: var(--bull);  background: var(--bull-soft); }
    .rec-HOLD { color: var(--ink);  border-color: var(--ink);   background: var(--paper-card); }
    .rec-SELL { color: var(--bear); border-color: var(--bear);  background: var(--bear-soft); }

    /* Section headings */
    .section {
        font-family: var(--sans); font-size: 11px; font-weight: 700;
        letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-2);
        margin: 32px 0 12px 0; padding-bottom: 6px;
        border-bottom: 1px solid var(--rule);
    }

    /* KPI / data tiles */
    .tile {
        background: var(--paper-card); border: 1px solid var(--rule-strong);
        padding: 14px 16px; min-height: 90px;
    }
    .tile-label {
        font-family: var(--sans); font-size: 11px; color: var(--ink-2);
        text-transform: uppercase; letter-spacing: 0.12em; font-weight: 600;
        margin-bottom: 6px;
    }
    .tile-value {
        font-family: var(--mono); font-size: 26px; color: var(--ink);
        font-weight: 500; font-feature-settings: 'tnum' 1;
        letter-spacing: -0.01em; line-height: 1.1;
    }
    .tile-sub {
        font-family: var(--mono); font-size: 11px; color: var(--ink-3);
        margin-top: 4px; font-feature-settings: 'tnum' 1;
    }
    .tile-value.bull { color: var(--bull); }
    .tile-value.bear { color: var(--bear); }

    /* Body text */
    .body {
        font-family: var(--sans); font-size: 15px; line-height: 1.65;
        color: var(--ink); max-width: 680px;
    }
    .body p, .body li { color: var(--ink); }
    .body strong, .body b { color: var(--ink); font-weight: 600; }

    /* Memo prose */
    .memo-prose {
        font-family: var(--serif); font-size: 18px; line-height: 1.55;
        color: var(--ink); max-width: 680px; font-style: italic;
        padding: 8px 0;
    }

    /* Mono numbers helper */
    .num { font-family: var(--mono); font-feature-settings: 'tnum' 1; }
    .bull-text { color: var(--bull); }
    .bear-text { color: var(--bear); }

    /* Risk pill */
    .risk-pill {
        font-family: var(--mono); font-size: 10px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.08em;
        padding: 3px 8px; margin-right: 10px; display: inline-block;
        border: 1px solid;
    }
    .risk-high   { color: var(--bear); border-color: var(--bear); background: var(--bear-soft); }
    .risk-medium { color: var(--ink-2); border-color: var(--ink-2); background: var(--paper-dim); }
    .risk-low    { color: var(--bull); border-color: var(--bull); background: var(--bull-soft); }

    .risk-card {
        background: var(--paper-card); border: 1px solid var(--rule);
        padding: 12px 14px; margin-bottom: 8px;
    }
    .risk-text { color: var(--ink); font-size: 14px; }
    .risk-source { color: var(--ink-3); font-family: var(--mono);
                   font-size: 11px; margin-top: 6px; text-transform: uppercase;
                   letter-spacing: 0.05em; }

    /* Sentiment chip */
    .sent {
        font-family: var(--mono); font-size: 11px; font-weight: 700;
        padding: 4px 10px; text-transform: uppercase; letter-spacing: 0.08em;
        display: inline-block; border: 1px solid;
    }
    .sent-positive { color: var(--bull); border-color: var(--bull); background: var(--bull-soft); }
    .sent-neutral  { color: var(--ink-2); border-color: var(--rule-strong); background: var(--paper-card); }
    .sent-negative { color: var(--bear); border-color: var(--bear); background: var(--bear-soft); }

    /* News card */
    .news-card {
        background: var(--paper-card); border: 1px solid var(--rule);
        border-left: 3px solid var(--coral);
        padding: 12px 14px; margin-bottom: 8px;
        transition: background 150ms ease;
    }
    .news-card:hover { background: var(--paper-dim); }
    .news-card a { color: var(--ink) !important; text-decoration: none;
                   font-size: 14px; font-weight: 500; line-height: 1.4; }
    .news-card a:hover { text-decoration: underline; text-decoration-color: var(--coral);
                         text-underline-offset: 3px; }
    .news-pub { color: var(--ink-3); font-family: var(--mono); font-size: 11px;
                margin-top: 6px; text-transform: uppercase; letter-spacing: 0.05em; }
    .news-cta { color: var(--coral); font-family: var(--mono); font-size: 10px;
                margin-top: 4px; text-transform: uppercase; letter-spacing: 0.1em;
                font-weight: 700; }

    /* Terminal panel for agent activity */
    .terminal-pane {
        background: var(--terminal); border: 1px solid var(--terminal-2);
        padding: 16px 20px; font-family: var(--mono); font-size: 13px;
        color: var(--phosphor);
        background-image: repeating-linear-gradient(
            0deg, rgba(111,227,154,0.04) 0px, rgba(111,227,154,0.04) 1px,
            transparent 1px, transparent 3px
        );
    }
    .agent-row {
        display: flex; align-items: center; padding: 8px 0;
        border-bottom: 1px dashed rgba(111,227,154,0.15);
        font-family: var(--mono); font-size: 13px;
    }
    .agent-row:last-child { border-bottom: none; }
    .agent-status { width: 24px; font-size: 14px; }
    .agent-name { color: var(--phosphor); font-weight: 700; width: 110px;
                  text-transform: uppercase; letter-spacing: 0.05em; }
    .agent-desc { color: rgba(111,227,154,0.7); flex: 1; }
    .agent-time { color: rgba(111,227,154,0.5); min-width: 55px; text-align: right; }
    @keyframes blink { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }
    .agent-running .agent-status { animation: blink 800ms ease-in-out infinite; }

    /* Progress bar override (cream paper version) */
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
    .stButton>button {
        background: var(--ink) !important; color: var(--paper) !important;
        border: 1px solid var(--ink) !important; border-radius: 4px !important;
        padding: 0.6rem 1.4rem !important; font-family: var(--sans) !important;
        font-weight: 500 !important; font-size: 14px !important;
        letter-spacing: 0.01em; transition: all 120ms ease;
    }
    .stButton>button:hover {
        background: var(--coral) !important; border-color: var(--coral) !important;
        transform: translateY(-1px);
    }
    .stButton>button:active { transform: translateY(0); }

    /* Expanders */
    div[data-testid="stExpander"] {
        background: var(--paper-card); border: 1px solid var(--rule);
        border-radius: 4px; margin: 6px 0;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary p,
    .streamlit-expanderHeader, .streamlit-expanderHeader p {
        color: var(--ink) !important; font-family: var(--sans) !important;
        font-size: 13px !important; font-weight: 500 !important;
    }
    div[data-testid="stExpander"] details summary:hover { background: var(--paper-dim); }

    /* Detail cards inside expanders */
    .detail-card {
        background: var(--paper); border: 1px solid var(--rule);
        padding: 10px 12px; margin: 6px 0;
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

    /* Footer */
    .footer {
        margin-top: 56px; padding: 28px 0 16px 0;
        border-top: 1px solid var(--rule-strong); color: var(--ink-2);
    }
    .footer-grid {
        display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 32px;
        margin-bottom: 20px;
    }
    .footer h4 {
        color: var(--ink) !important; font-family: var(--sans);
        font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em;
        font-weight: 700; margin-bottom: 8px;
    }
    .footer-text {
        color: var(--ink-2); font-size: 13px; line-height: 1.65;
    }
    .footer-bottom {
        text-align: center; padding-top: 16px;
        border-top: 1px solid var(--rule); color: var(--ink-3);
        font-family: var(--mono); font-size: 11px; letter-spacing: 0.05em;
    }

    /* Empty state */
    .empty {
        background: var(--paper-card); border: 1px solid var(--rule);
        padding: 56px 40px; text-align: center; margin: 24px 0;
    }
    .empty-title {
        font-family: var(--serif); font-size: 32px; color: var(--ink);
        line-height: 1.2; margin-bottom: 12px;
    }
    .empty-body {
        font-family: var(--sans); font-size: 15px; color: var(--ink-2);
        max-width: 520px; margin: 0 auto; line-height: 1.6;
    }
    .empty-tickers {
        font-family: var(--mono); margin-top: 14px;
        color: var(--ink); font-weight: 700; letter-spacing: 0.04em;
    }

    /* Pull-quote / valuation commentary */
    .pull-quote {
        font-family: var(--serif); font-size: 19px; line-height: 1.5;
        color: var(--ink); padding: 8px 0 8px 18px;
        border-left: 3px solid var(--coral); max-width: 680px;
    }

    /* Chart container */
    .chart-frame {
        background: var(--paper-card); border: 1px solid var(--rule);
        padding: 14px 16px; margin-bottom: 12px;
    }
    .chart-label {
        font-family: var(--sans); font-size: 11px; color: var(--ink-2);
        text-transform: uppercase; letter-spacing: 0.12em; font-weight: 600;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state for pipeline result
if "result" not in st.session_state:
    st.session_state.result = None
if "ticker_done" not in st.session_state:
    st.session_state.ticker_done = None

# ── Masthead ────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="masthead">
        <div class="masthead-left">
            <span class="wordmark">Loli<span class="accent">F</span>in</span>
            <span class="tagline">Agentic equity research</span>
        </div>
        <div class="masthead-right">
            A project by <b>Iolanda Costa</b><br>
            <span style="color:var(--ink-3);">M.Sc. Finance &amp; AI · Bologna Business School</span>
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
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.2f}T"
    if abs(v) >= 1000:
        return f"${v/1000:.2f}B"
    return f"${v:,.0f}M"


def fmt_pct(v, signed=False):
    if v is None or not isinstance(v, (int, float)):
        return "—"
    pct = v * 100 if abs(v) < 5 else v
    s = f"{pct:+.1f}%" if signed else f"{pct:.1f}%"
    return s.replace("-", "−")  # proper minus sign


def fmt_signed_pct(v):
    return fmt_pct(v, signed=True)


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


# ── Agents with substeps ─────────────────────────────────────────────────
AGENTS = [
    ("filings",   "Filings",   "Pulling fundamentals from Yahoo Finance"),
    ("news",      "News",      "Scanning recent headlines"),
    ("valuation", "Valuation", "Running DCF + comparable multiples"),
    ("risk",      "Risk",      "Cross-referencing red flags"),
    ("editor",    "Editor",    "Composing the memo"),
]
AGENT_KEYS = [a[0] for a in AGENTS]


def render_progress(container, statuses, timings, in_terminal=True):
    """Render the live progress card."""
    rows = []
    for key, name, desc in AGENTS:
        s = statuses.get(key, "pending")
        if s == "done":
            icon, row_cls = "●", ""
        elif s == "running":
            icon, row_cls = "◐", "agent-running"
        else:
            icon, row_cls = "○", ""
        if s == "done":
            current_desc = "complete"
        else:
            current_desc = desc
        t = timings.get(key, "")
        t_html = f'<span class="agent-time">{t}</span>' if t else ""
        rows.append(
            f'<div class="agent-row {row_cls}">'
            f'<span class="agent-status">{icon}</span>'
            f'<span class="agent-name">{name}</span>'
            f'<span class="agent-desc">{current_desc}</span>'
            f'{t_html}</div>'
        )
    inner = "".join(rows)
    if in_terminal:
        inner = f'<div class="terminal-pane">{inner}</div>'
    container.markdown(inner, unsafe_allow_html=True)


# ── Run pipeline ─────────────────────────────────────────────────────────
if run:
    if not ticker:
        st.error("Enter a ticker.")
        st.stop()

    st.markdown('<div class="section">Pipeline · live</div>', unsafe_allow_html=True)
    progress_bar = st.progress(0, text="Initializing 5-agent pipeline")
    progress_box = st.empty()

    statuses = {}
    timings = {}
    render_progress(progress_box, statuses, timings)

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
                    if next_idx < total:
                        nk = AGENT_KEYS[next_idx]
                        if statuses.get(nk) is None:
                            statuses[nk] = "running"
                    render_progress(progress_box, statuses, timings)
                if isinstance(node_output, dict):
                    for k, v in node_output.items():
                        if k == "errors":
                            result.setdefault("errors", []).extend(v or [])
                        else:
                            result[k] = v

        for k in AGENT_KEYS:
            if statuses.get(k) != "done": statuses[k] = "done"
        progress_bar.progress(100, text=f"Complete · {time.time() - pipeline_start:.1f}s total")
        render_progress(progress_box, statuses, timings)
        time.sleep(0.4)
        progress_bar.empty()
        progress_box.empty()
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        st.stop()

    result["ticker"] = ticker
    result["_timings"] = timings
    result["_total_time"] = time.time() - pipeline_start
    st.session_state.result = result
    st.session_state.ticker_done = ticker


# ── Render results from session ─────────────────────────────────────────
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

    # ── Hero ────────────────────────────────────────────────────
    upside = val.get("upside_pct")
    upside_class = "bull" if (isinstance(upside, (int, float)) and upside > 0) else (
        "bear" if (isinstance(upside, (int, float)) and upside < 0) else ""
    )
    upside_str = fmt_signed_pct(upside) if upside is not None else "—"

    st.markdown(
        f"""
        <div class="memo-hero">
            <div class="memo-h-row">
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
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI row ──────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(tile("Current price",
                         f"${val.get('current_price'):.2f}" if val.get('current_price') else "—"),
                    unsafe_allow_html=True)
    with c2:
        fv = val.get("blended_fair_value")
        dcf = val.get("dcf_fair_value"); comp = val.get("comp_fair_value")
        if dcf and comp: sub = f"DCF ${dcf} · Comps ${comp}"
        elif dcf: sub = f"DCF ${dcf}"
        elif comp: sub = f"Comps ${comp}"
        else: sub = ""
        st.markdown(tile("Fair value", f"${fv:.2f}" if fv else "—", sub),
                    unsafe_allow_html=True)
    with c3:
        st.markdown(tile("Upside", upside_str, "vs current price", value_class=upside_class),
                    unsafe_allow_html=True)
    with c4:
        rs_display = f"{risk_score}/10" if risk_score else "—"
        st.markdown(tile("Risk score", rs_display, risk_label(risk_score)),
                    unsafe_allow_html=True)

    # KPI expanders (separate row so no overlap with tiles)
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
                f"<b>Blended</b> = average of DCF and Comps.</div>",
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
                    f"<span class='bear-text'><b>{sc['high']} high</b></span> · "
                    f"<b>{sc['medium']} medium</b> · "
                    f"<span class='bull-text'><b>{sc['low']} low</b></span><br/><br/>"
                    f"Score (1 safe → 10 avoid) blends count, severity mix, and "
                    f"source diversity across filings, news, and valuation.</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("<div class='body'>No risks identified.</div>", unsafe_allow_html=True)

    # ── Charts row 1: Price history + Valuation comparison ─────
    st.markdown('<div class="section">Visuals</div>', unsafe_allow_html=True)
    chart_left, chart_right = st.columns([1.4, 1])

    with chart_left:
        st.markdown('<div class="chart-label">6-month price history</div>', unsafe_allow_html=True)
        if price_history and len(price_history) > 0:
            df = pd.DataFrame(price_history)
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
            try:
                line = (
                    alt.Chart(df.reset_index())
                    .mark_line(color="#FF5B3C", strokeWidth=2)
                    .encode(
                        x=alt.X("date:T", title=None,
                                axis=alt.Axis(labelColor="#5C544A", grid=False,
                                              tickColor="#5C544A", domainColor="#1A1714")),
                        y=alt.Y("close:Q", title=None,
                                scale=alt.Scale(zero=False),
                                axis=alt.Axis(labelColor="#5C544A",
                                              gridColor="rgba(26,23,20,0.08)",
                                              tickColor="#5C544A", domainColor="#1A1714",
                                              format="$.0f")),
                        tooltip=[alt.Tooltip("date:T", title="Date"),
                                 alt.Tooltip("close:Q", title="Close", format="$.2f")],
                    )
                    .properties(height=260)
                    .configure_view(strokeWidth=0, fill="#FBF6EE")
                    .configure_axis(labelFont="JetBrains Mono", titleFont="Geist")
                )
                st.altair_chart(line, use_container_width=True)
            except Exception:
                # Fallback to native Streamlit chart
                st.line_chart(df["close"], height=260, color="#FF5B3C")
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
                                axis=alt.Axis(labelColor="#1A1714", labelAngle=0,
                                              labelFont="JetBrains Mono", labelFontSize=11,
                                              domainColor="#1A1714", tickColor="#5C544A")),
                        y=alt.Y("value:Q", title=None,
                                axis=alt.Axis(labelColor="#5C544A",
                                              gridColor="rgba(26,23,20,0.08)",
                                              format="$.0f")),
                        color=alt.Color("method:N", scale=alt.Scale(
                            domain=["Current", "DCF", "Comps", "Blended"],
                            range=["#5C544A", "#1F7A4D", "#F5C842", "#FF5B3C"],
                        ), legend=None),
                        tooltip=[alt.Tooltip("method"), alt.Tooltip("value:Q", format="$.2f")],
                    )
                    .properties(height=260)
                    .configure_view(strokeWidth=0, fill="#FBF6EE")
                )
                st.altair_chart(bar, use_container_width=True)
            except Exception:
                st.bar_chart(bdf.set_index("method"))
        else:
            st.markdown("<div class='body'>Valuation data unavailable.</div>", unsafe_allow_html=True)

    # ── Charts row 2: margins / cash-debt / risk donut ───────────
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
                    .mark_bar(size=30)
                    .encode(
                        y=alt.Y("type:N", title=None, sort=None,
                                axis=alt.Axis(labelColor="#1A1714", labelFont="Geist", labelFontSize=12)),
                        x=alt.X("value:Q", title=None,
                                scale=alt.Scale(domain=[0, 100]),
                                axis=alt.Axis(labelColor="#5C544A",
                                              gridColor="rgba(26,23,20,0.08)", format=".0f")),
                        color=alt.value("#1F7A4D"),
                        tooltip=[alt.Tooltip("type"), alt.Tooltip("value:Q", format=".1f", title="%")],
                    )
                    .properties(height=180)
                    .configure_view(strokeWidth=0, fill="#FBF6EE")
                )
                st.altair_chart(mc, use_container_width=True)
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
                                axis=alt.Axis(labelColor="#1A1714", labelAngle=0, labelFont="Geist")),
                        y=alt.Y("value:Q", title=None,
                                axis=alt.Axis(labelColor="#5C544A",
                                              gridColor="rgba(26,23,20,0.08)", format="$,.0f")),
                        color=alt.Color("type:N", scale=alt.Scale(
                            domain=["Cash", "Debt"], range=["#1F7A4D", "#C2391C"]), legend=None),
                        tooltip=[alt.Tooltip("type"), alt.Tooltip("value:Q", format="$,.0f", title="$M")],
                    )
                    .properties(height=180)
                    .configure_view(strokeWidth=0, fill="#FBF6EE")
                )
                st.altair_chart(cc, use_container_width=True)
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
                        .mark_arc(innerRadius=42, outerRadius=78, stroke="#FBF6EE", strokeWidth=2)
                        .encode(
                            theta=alt.Theta("count:Q"),
                            color=alt.Color("severity:N", scale=alt.Scale(
                                domain=["high", "medium", "low"],
                                range=["#C2391C", "#5C544A", "#1F7A4D"],
                            ), legend=alt.Legend(orient="bottom", labelColor="#1A1714",
                                                  title=None, labelFont="Geist", labelFontSize=11)),
                            tooltip=["severity", "count"],
                        )
                        .properties(height=180)
                        .configure_view(strokeWidth=0, fill="#FBF6EE")
                    )
                    st.altair_chart(donut, use_container_width=True)
                except Exception:
                    st.bar_chart(rdf.set_index("severity"))
        else:
            st.markdown("<div class='body'>No risks to chart.</div>", unsafe_allow_html=True)

    # ── Two-column body ────────────────────────────────────────────
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
            growth = fins.get("revenue_growth_yoy")
            growth_cls = "bull" if (isinstance(growth, (int, float)) and growth > 0) else (
                "bear" if (isinstance(growth, (int, float)) and growth < 0) else ""
            )
            st.markdown(tile("Revenue growth (YoY)", fmt_signed_pct(growth) if growth else "—",
                             value_class=growth_cls), unsafe_allow_html=True)

        with st.expander("More fundamentals"):
            st.markdown(
                f"<div class='detail-card'><div class='detail-label'>Market cap</div>"
                f"<div class='detail-value'>{fmt_money(fins.get('market_cap'))}</div></div>"
                f"<div class='detail-card'><div class='detail-label'>Gross margin</div>"
                f"<div class='detail-value'>{fmt_pct(fins.get('gross_margin'))}</div></div>"
                f"<div class='detail-card'><div class='detail-label'>Cash on hand</div>"
                f"<div class='detail-value'>{fmt_money(fins.get('cash'))}</div></div>"
                f"<div class='detail-card'><div class='detail-label'>Trailing P/E</div>"
                f"<div class='detail-value'>{fins.get('trailing_pe'):.1f}x</div></div>"
                if fins.get('trailing_pe') else
                f"<div class='detail-card'><div class='detail-label'>Trailing P/E</div>"
                f"<div class='detail-value'>—</div></div>",
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section">Valuation commentary</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="pull-quote">{result.get("valuation_notes") or "—"}</div>',
            unsafe_allow_html=True,
        )

        if fins.get("summary"):
            st.markdown('<div class="section">Business summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="body">{fins["summary"]}</div>', unsafe_allow_html=True)

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
        st.markdown(
            f'<div class="body" style="margin-top:10px;">{result.get("news_summary") or "—"}</div>',
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
                f'<div class="news-card">'
                f'<a href="{url}" target="_blank" rel="noopener">{title}</a>'
                f'<div class="news-pub">{pub}</div>'
                f'<div class="news-cta">Read article →</div></div>',
                unsafe_allow_html=True,
            )

    # ── Deep dive ─────────────────────────────────────────────
    st.markdown('<div class="section">Deep dive</div>', unsafe_allow_html=True)
    if result.get("memo_markdown"):
        with st.expander("Full investment memo", expanded=False):
            st.markdown(
                f"<div class='body'>{result['memo_markdown']}</div>",
                unsafe_allow_html=True,
            )

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
                    f'<div class="news-card">'
                    f'<a href="{s.get("url") or "#"}" target="_blank">{s.get("title", "")}</a>'
                    f'<div class="news-pub">{s.get("publisher") or ""}</div></div>',
                    unsafe_allow_html=True,
                )
        with tabs[2]:
            for k, v in (val or {}).items():
                if k == "assumptions":
                    st.markdown(
                        f"<div class='detail-card'><div class='detail-label'>Assumptions</div>"
                        f"<div class='detail-value' style='font-size:13px;'>"
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
    statuses_done = {k: "done" for k in AGENT_KEYS}
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
    # ── Empty state ────────────────────────────────────────────
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
