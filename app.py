"""
LoliFin — Streamlit dashboard.

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

# ── Global CSS ───────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp { background: #0a0e1a; color: #e5e7eb; }
    #MainMenu, footer, header { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none; }

    /* Force readable text everywhere */
    .stApp p, .stApp li, .stApp span, .stApp div,
    .stMarkdown, .stMarkdown p, .stMarkdown li,
    .stMarkdown strong { color: #e5e7eb; }
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown h4, .stMarkdown h5 { color: #ffffff !important; }

    /* Brand bar */
    .brand-bar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 18px 26px; margin: -1rem -1rem 1.5rem -1rem;
        background: linear-gradient(90deg, #0b1437 0%, #1a2b6b 60%, #2541b2 100%);
        border-bottom: 1px solid #2a3a7a;
    }
    .brand-name { color: #fff; font-size: 1.7rem; font-weight: 700; letter-spacing: -0.02em; }
    .brand-tag { color: #9fb4ff; font-size: 0.88rem; font-weight: 500; }
    .brand-credit {
        color: #cfd9ff; font-size: 0.82rem; text-align: right;
        background: rgba(255,255,255,0.06); padding: 8px 14px; border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.12);
    }
    .brand-credit b { color: #fff; }

    /* KPI cards */
    .kpi {
        background: #161b2c; border: 1px solid #2a3142; border-radius: 12px;
        padding: 18px 20px; height: 100%;
    }
    .kpi-label {
        color: #9ca3af; font-size: 0.72rem; font-weight: 700;
        letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 8px;
    }
    .kpi-value { color: #ffffff !important; font-size: 1.6rem; font-weight: 700; line-height: 1.2; }
    .kpi-sub { color: #9ca3af; font-size: 0.78rem; margin-top: 6px; }

    /* Recommendation badge */
    .rec-badge {
        display: inline-block; padding: 10px 22px; border-radius: 8px;
        font-weight: 700; font-size: 1.15rem; letter-spacing: 0.05em;
    }
    .rec-BUY { background: #052e1f; color: #34d399; border: 1.5px solid #34d399; }
    .rec-HOLD { background: #2d2208; color: #fbbf24; border: 1.5px solid #fbbf24; }
    .rec-SELL { background: #2d0a0a; color: #f87171; border: 1.5px solid #f87171; }

    /* Section header */
    .section-h {
        color: #ffffff !important; font-size: 1.1rem; font-weight: 600;
        margin: 1.8rem 0 0.9rem 0; padding-bottom: 8px;
        border-bottom: 1px solid #2a3142;
    }

    /* Body text */
    .body { color: #d1d5db !important; font-size: 0.95rem; line-height: 1.65; }
    .body p { color: #d1d5db !important; }

    /* Risk pill */
    .risk-pill {
        display: inline-block; padding: 3px 10px; border-radius: 12px;
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.06em;
        text-transform: uppercase; margin-right: 10px;
    }
    .risk-high { background: #2d0a0a; color: #f87171; }
    .risk-medium { background: #2d2208; color: #fbbf24; }
    .risk-low { background: #052e1f; color: #34d399; }

    .risk-card {
        background: #161b2c; border: 1px solid #2a3142; border-radius: 8px;
        padding: 14px 16px; margin-bottom: 10px;
    }
    .risk-card-text { color: #e5e7eb !important; font-size: 0.95rem; }

    /* Sentiment chip */
    .sent {
        display: inline-block; padding: 5px 14px; border-radius: 14px;
        font-size: 0.78rem; font-weight: 600;
    }
    .sent-positive { background: #052e1f; color: #34d399; }
    .sent-neutral { background: #1f2937; color: #d1d5db; }
    .sent-negative { background: #2d0a0a; color: #f87171; }

    /* News card */
    .news-card {
        background: #161b2c; border-left: 3px solid #4b6bfb;
        padding: 12px 14px; margin-bottom: 10px; border-radius: 4px;
        transition: all 0.15s ease;
    }
    .news-card:hover { background: #1c2238; border-left-color: #6d8bff; }
    .news-card a { color: #e5e7eb !important; text-decoration: none; font-size: 0.93rem; font-weight: 500; }
    .news-card a:hover { color: #fff !important; }
    .news-pub { color: #9ca3af; font-size: 0.72rem; margin-top: 4px; }
    .news-cta { color: #6d8bff; font-size: 0.7rem; margin-top: 6px;
                text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; }

    /* Agent progress rows */
    .agent-row {
        display: flex; align-items: center; padding: 11px 14px;
        background: #161b2c; border: 1px solid #2a3142; border-radius: 8px;
        margin-bottom: 8px; font-size: 0.92rem;
    }
    .agent-status { width: 28px; font-size: 1.15rem; text-align: center; }
    .agent-name { color: #fff; font-weight: 600; width: 130px; }
    .agent-desc { color: #9ca3af; flex: 1; font-size: 0.88rem; }
    .agent-time { color: #6b7280; font-size: 0.78rem; min-width: 50px; text-align: right; }

    /* Progress bar inside agent rows */
    @keyframes pulse-glow {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    .agent-running .agent-status { animation: pulse-glow 1.2s ease-in-out infinite; }

    /* Streamlit progress bar override */
    .stProgress > div > div { background: linear-gradient(90deg, #4b6bfb, #34d399) !important; }
    .stProgress > div { background: #1f2937 !important; }

    /* Inputs */
    .stTextInput input {
        background: #161b2c !important; color: #fff !important;
        border: 1px solid #2a3142 !important; border-radius: 10px !important;
        padding: 0.6rem 0.9rem !important; font-size: 1rem !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #4b6bfb 0%, #6d8bff 100%) !important;
        color: #fff !important; border: none !important; border-radius: 10px !important;
        padding: 0.6rem 1.6rem !important; font-weight: 600 !important;
        font-size: 1rem !important;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #3b5beb 0%, #5d7bff 100%) !important;
    }

    /* Expander */
    .streamlit-expanderHeader,
    .streamlit-expanderHeader p { color: #e5e7eb !important; font-weight: 500 !important; }
    div[data-testid="stExpander"] {
        background: #161b2c; border: 1px solid #2a3142; border-radius: 8px;
        margin-bottom: 8px;
    }
    div[data-testid="stExpander"] details summary { color: #e5e7eb !important; }

    /* Detail cards inside expanders */
    .detail-card { background: #1c2238; border-radius: 8px; padding: 12px 14px; margin: 8px 0; }
    .detail-label { color: #9ca3af; font-size: 0.72rem; text-transform: uppercase;
                    letter-spacing: 0.08em; font-weight: 700; }
    .detail-value { color: #fff; font-size: 1.05rem; font-weight: 600; margin-top: 2px; }

    /* Clickable KPI */
    .kpi-clickable { cursor: pointer; transition: all 0.15s; }
    .kpi-clickable:hover { border-color: #4b6bfb; transform: translateY(-1px); }

    /* Footer */
    .footer {
        margin-top: 3rem; padding: 1.6rem 0 1rem 0;
        border-top: 1px solid #2a3142; color: #9ca3af;
    }
    .footer-grid {
        display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 2rem;
        margin-bottom: 1rem;
    }
    .footer h4 { color: #fff !important; font-size: 0.95rem; margin-bottom: 0.6rem; }
    .footer-text { color: #9ca3af; font-size: 0.85rem; line-height: 1.7; }
    .footer-bottom { text-align: center; padding-top: 1rem;
                     border-top: 1px solid #2a3142; color: #6b7280; font-size: 0.78rem; }

    /* Make memo markdown links blue */
    .memo-box a, .body a { color: #6d8bff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Brand bar ────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="brand-bar">
        <div>
            <span class="brand-name">LoliFin</span>
            <span class="brand-tag">  ·  Agentic Equity Research</span>
        </div>
        <div class="brand-credit">
            A project by <b>Iolanda Costa</b><br>
            <span style="font-size: 0.74rem; color: #9fb4ff;">
                M.Sc. Finance &amp; AI · Bologna Business School
            </span>
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
    run = st.button("Generate", type="primary", use_container_width=True)


# ── Helpers ──────────────────────────────────────────────────────────────
def kpi_card(label, value, sub=""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>{sub_html}</div>'
    )


def fmt_money(v):
    if v is None or not isinstance(v, (int, float)):
        return "—"
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.2f}T"
    if abs(v) >= 1000:
        return f"${v/1000:.2f}B"
    return f"${v:,.0f}M"


def fmt_pct(v):
    if v is None or not isinstance(v, (int, float)):
        return "—"
    return f"{v*100:.1f}%" if abs(v) < 5 else f"{v:.1f}%"


def risk_label(score):
    if score is None:
        return "—"
    if score <= 3:
        return "low risk"
    if score <= 6:
        return "moderate"
    return "elevated"


# ── Agents definition with sub-tasks for progress display ────────────────
AGENTS = [
    ("filings",   "Filings",   [
        "Connecting to Yahoo Finance",
        "Fetching fundamentals (revenue, FCF, margins, debt)",
        "Pulling 6-month price history",
        "Asking LLM for business summary",
    ]),
    ("news",      "News",      [
        "Pulling recent headlines from Yahoo",
        "Normalizing publisher and URL data",
        "Sending to LLM for sentiment classification",
    ]),
    ("valuation", "Valuation", [
        "Computing 5-year DCF projection",
        "Calculating comparable multiples (sector P/E)",
        "Blending DCF + comps into fair value",
        "Asking LLM to narrate the result",
    ]),
    ("risk",      "Risk",      [
        "Reading filings + news + valuation context",
        "Cross-referencing red-flag patterns",
        "Asking LLM to rank severities",
        "Falling back to deterministic rules if needed",
    ]),
    ("editor",    "Editor",    [
        "Aggregating outputs from all four agents",
        "Computing Buy/Hold/Sell deterministically",
        "Composing the final memo prose",
    ]),
]
AGENT_KEYS = [a[0] for a in AGENTS]


def render_progress(container, statuses, current_substeps, timings):
    """Render the live progress card."""
    rows = []
    for key, name, substeps in AGENTS:
        s = statuses.get(key, "pending")
        if s == "done":
            icon, color, row_cls = "●", "#34d399", ""
        elif s == "running":
            icon, color, row_cls = "◐", "#4b6bfb", "agent-running"
        else:
            icon, color, row_cls = "○", "#4b5563", ""
        desc = current_substeps.get(key) or (substeps[0] if s == "pending" else "Done")
        if s == "done":
            desc = "Done"
        t = timings.get(key, "")
        t_html = f'<span class="agent-time">{t}</span>' if t else ""
        rows.append(
            f'<div class="agent-row {row_cls}">'
            f'<span class="agent-status" style="color:{color};">{icon}</span>'
            f'<span class="agent-name">{name}</span>'
            f'<span class="agent-desc">{desc}</span>'
            f'{t_html}</div>'
        )
    container.markdown("".join(rows), unsafe_allow_html=True)


# ── Render results ──────────────────────────────────────────────────────
if run:
    if not ticker:
        st.error("Enter a ticker.")
        st.stop()

    st.markdown('<div class="section-h">Pipeline Progress</div>', unsafe_allow_html=True)
    progress_bar = st.progress(0, text="Starting 5-agent pipeline…")
    progress_box = st.empty()

    statuses = {}
    timings = {}
    substeps = {}
    render_progress(progress_box, statuses, substeps, timings)

    result = {}
    pipeline_start = time.time()
    completed = 0
    total = len(AGENT_KEYS)

    # Mark first agent as running immediately for visual feedback
    statuses[AGENT_KEYS[0]] = "running"
    substeps[AGENT_KEYS[0]] = AGENTS[0][2][0]
    render_progress(progress_box, statuses, substeps, timings)

    try:
        for event in graph.stream({"ticker": ticker}, stream_mode="updates"):
            for node_name, node_output in event.items():
                if node_name in AGENT_KEYS:
                    elapsed = time.time() - pipeline_start
                    statuses[node_name] = "done"
                    timings[node_name] = f"{elapsed:.1f}s"
                    completed += 1
                    # Update progress bar
                    pct = int((completed / total) * 100)
                    progress_bar.progress(pct, text=f"{completed}/{total} agents complete · {elapsed:.1f}s elapsed")
                    # Mark next pending as running
                    next_idx = AGENT_KEYS.index(node_name) + 1
                    if next_idx < total:
                        next_key = AGENT_KEYS[next_idx]
                        if statuses.get(next_key) is None:
                            statuses[next_key] = "running"
                            substeps[next_key] = AGENTS[next_idx][2][0]
                    # Mark any other parallel-running pending as running
                    for k in AGENT_KEYS:
                        if statuses.get(k) is None:
                            # Don't mark editor early — keep order
                            pass
                    render_progress(progress_box, statuses, substeps, timings)
                if isinstance(node_output, dict):
                    for k, v in node_output.items():
                        if k == "errors":
                            result.setdefault("errors", []).extend(v or [])
                        else:
                            result[k] = v

        # Final state
        for k in AGENT_KEYS:
            if statuses.get(k) != "done":
                statuses[k] = "done"
        progress_bar.progress(100, text=f"All agents complete · {time.time() - pipeline_start:.1f}s total")
        render_progress(progress_box, statuses, substeps, timings)
        time.sleep(0.3)
        progress_bar.empty()

    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        st.stop()

    result["ticker"] = ticker

    company = result.get("company_name") or ticker
    rec = result.get("recommendation") or "HOLD"
    val = result.get("valuation") or {}
    fins = result.get("financials") or {}
    risks = result.get("risks") or []
    risk_score = result.get("risk_score")
    sentiment = (result.get("news_sentiment") or "neutral").lower()
    price_history = result.get("price_history") or []

    # ── Headline + recommendation ──────────────────────────────
    st.markdown('<div class="section-h">Memo</div>', unsafe_allow_html=True)
    h_left, h_right = st.columns([3, 1])
    with h_left:
        st.markdown(
            f"<h2 style='margin-bottom:0;'>{company} "
            f"<span style='color:#9ca3af;font-size:1.1rem;font-weight:500;'>"
            f"({ticker})</span></h2>"
            f"<div style='color:#9ca3af;font-size:0.85rem;margin-top:4px;'>"
            f"{fins.get('sector') or ''}"
            f"{' · ' + fins.get('industry') if fins.get('industry') else ''}</div>",
            unsafe_allow_html=True,
        )
    with h_right:
        st.markdown(
            f"<div style='text-align:right;margin-top:8px;'>"
            f"<span class='rec-badge rec-{rec}'>{rec}</span></div>",
            unsafe_allow_html=True,
        )

    # ── KPI tiles (clickable expanders) ────────────────────────
    upside = val.get("upside_pct")
    upside_str = f"{upside:+.1f}%" if isinstance(upside, (int, float)) else "—"
    upside_color = "#34d399" if (isinstance(upside, (int, float)) and upside > 0) else (
        "#f87171" if (isinstance(upside, (int, float)) and upside < 0) else "#9ca3af"
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            kpi_card("Current Price",
                     f"${val.get('current_price'):.2f}" if val.get('current_price') else "—"),
            unsafe_allow_html=True,
        )
        with st.expander("Why this price?"):
            st.markdown(
                f"<div class='body'>Live mid-quote from Yahoo Finance. "
                f"Market cap: {fmt_money(fins.get('market_cap'))}. "
                f"Trailing P/E: {fins.get('trailing_pe'):.1f}x" if fins.get('trailing_pe') else "Trailing P/E: —",
                unsafe_allow_html=True,
            )

    with c2:
        fv = val.get("blended_fair_value")
        dcf = val.get("dcf_fair_value"); comp = val.get("comp_fair_value")
        sub = ""
        if dcf and comp: sub = f"DCF ${dcf} · Comps ${comp}"
        elif dcf: sub = f"DCF only: ${dcf}"
        elif comp: sub = f"Comps only: ${comp}"
        st.markdown(kpi_card("Fair Value", f"${fv:.2f}" if fv else "—", sub),
                    unsafe_allow_html=True)
        with st.expander("How was this calculated?"):
            assumptions = val.get("assumptions") or {}
            st.markdown(
                f"<div class='body'><b>DCF assumptions:</b><br>"
                f"• WACC: {(assumptions.get('wacc') or 0)*100:.1f}%<br>"
                f"• Growth: {(assumptions.get('growth') or 0)*100:.1f}%<br>"
                f"• Terminal multiple: {assumptions.get('terminal_multiple') or '—'}x<br>"
                f"• Sector P/E (for comps): {assumptions.get('sector_pe') or '—'}<br><br>"
                f"<b>Blended:</b> average of DCF and Comps methods.</div>",
                unsafe_allow_html=True,
            )

    with c3:
        st.markdown(
            f'<div class="kpi"><div class="kpi-label">Upside</div>'
            f'<div class="kpi-value" style="color:{upside_color} !important;">{upside_str}</div>'
            f'<div class="kpi-sub">vs current price</div></div>',
            unsafe_allow_html=True,
        )
        with st.expander("What does this mean?"):
            if isinstance(upside, (int, float)):
                direction = "above" if upside > 0 else "below"
                st.markdown(
                    f"<div class='body'>Blended fair value is "
                    f"<b>{abs(upside):.1f}% {direction}</b> the current price. "
                    f"Decision thresholds:<br>"
                    f"• Upside &gt; 15% AND risk score ≤ 5 → <b>BUY</b><br>"
                    f"• Upside &lt; -10% OR risk score ≥ 8 → <b>SELL</b><br>"
                    f"• Otherwise → <b>HOLD</b></div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("<div class='body'>Upside unavailable.</div>", unsafe_allow_html=True)

    with c4:
        rs_display = f"{risk_score}/10" if risk_score else "—"
        st.markdown(kpi_card("Risk Score", rs_display, risk_label(risk_score)),
                    unsafe_allow_html=True)
        with st.expander("Why this risk score?"):
            if risks:
                sev_counts = {"high": 0, "medium": 0, "low": 0}
                for r in risks:
                    sev = (r.get("severity") or "medium").lower()
                    if sev in sev_counts: sev_counts[sev] += 1
                st.markdown(
                    f"<div class='body'>{len(risks)} risks identified: "
                    f"<span style='color:#f87171'><b>{sev_counts['high']} high</b></span>, "
                    f"<span style='color:#fbbf24'><b>{sev_counts['medium']} medium</b></span>, "
                    f"<span style='color:#34d399'><b>{sev_counts['low']} low</b></span>.<br><br>"
                    f"Score (1=safe, 10=avoid) blends count, severity mix, and "
                    f"source diversity across filings, news, and valuation signals."
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("<div class='body'>No risks identified.</div>", unsafe_allow_html=True)

    # ── Charts row ─────────────────────────────────────────────
    st.markdown('<div class="section-h">Visuals</div>', unsafe_allow_html=True)

    chart_left, chart_right = st.columns([1.4, 1])

    with chart_left:
        st.markdown(
            "<div style='color:#9ca3af;font-size:0.78rem;font-weight:700;"
            "letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;'>"
            "6-Month Price History</div>",
            unsafe_allow_html=True,
        )
        if price_history:
            df = pd.DataFrame(price_history)
            df["date"] = pd.to_datetime(df["date"])
            min_p, max_p = df["close"].min(), df["close"].max()
            chart = (
                alt.Chart(df)
                .mark_area(
                    line={"color": "#6d8bff", "strokeWidth": 2},
                    color=alt.Gradient(
                        gradient="linear",
                        stops=[
                            alt.GradientStop(color="#6d8bff", offset=0),
                            alt.GradientStop(color="#0a0e1a", offset=1),
                        ],
                        x1=1, x2=1, y1=1, y2=0,
                    ),
                )
                .encode(
                    x=alt.X("date:T", title=None, axis=alt.Axis(labelColor="#9ca3af", grid=False)),
                    y=alt.Y("close:Q", title=None,
                            scale=alt.Scale(domain=[min_p * 0.95, max_p * 1.02]),
                            axis=alt.Axis(labelColor="#9ca3af", grid=True, gridColor="#1f2937")),
                    tooltip=[alt.Tooltip("date:T", title="Date"),
                             alt.Tooltip("close:Q", title="Close", format="$.2f")],
                )
                .properties(height=280, background="transparent")
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.markdown("<div class='body'>Price history unavailable.</div>", unsafe_allow_html=True)

    with chart_right:
        st.markdown(
            "<div style='color:#9ca3af;font-size:0.78rem;font-weight:700;"
            "letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;'>"
            "Valuation Comparison</div>",
            unsafe_allow_html=True,
        )
        bars = []
        if val.get("current_price"): bars.append({"method": "Current", "value": val["current_price"]})
        if val.get("dcf_fair_value"): bars.append({"method": "DCF", "value": val["dcf_fair_value"]})
        if val.get("comp_fair_value"): bars.append({"method": "Comps", "value": val["comp_fair_value"]})
        if val.get("blended_fair_value"): bars.append({"method": "Blended", "value": val["blended_fair_value"]})

        if bars:
            bdf = pd.DataFrame(bars)
            bar_chart = (
                alt.Chart(bdf)
                .mark_bar(cornerRadiusEnd=4, size=42)
                .encode(
                    x=alt.X("method:N", title=None, sort=None,
                            axis=alt.Axis(labelColor="#e5e7eb", labelAngle=0)),
                    y=alt.Y("value:Q", title=None,
                            axis=alt.Axis(labelColor="#9ca3af", gridColor="#1f2937")),
                    color=alt.Color("method:N", scale=alt.Scale(
                        domain=["Current", "DCF", "Comps", "Blended"],
                        range=["#9ca3af", "#4b6bfb", "#8b5cf6", "#34d399"],
                    ), legend=None),
                    tooltip=[alt.Tooltip("method"), alt.Tooltip("value:Q", format="$.2f")],
                )
                .properties(height=280, background="transparent")
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(bar_chart, use_container_width=True)
        else:
            st.markdown("<div class='body'>Valuation data unavailable.</div>", unsafe_allow_html=True)

    # ── Second visual row: margins gauges + cash vs debt + risk donut ─
    v1, v2, v3 = st.columns(3)

    with v1:
        st.markdown(
            "<div style='color:#9ca3af;font-size:0.78rem;font-weight:700;"
            "letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;'>"
            "Margins</div>",
            unsafe_allow_html=True,
        )
        m_data = []
        if fins.get("gross_margin") is not None:
            m_data.append({"type": "Gross", "value": fins["gross_margin"] * 100})
        if fins.get("operating_margin") is not None:
            m_data.append({"type": "Operating", "value": fins["operating_margin"] * 100})
        if m_data:
            mdf = pd.DataFrame(m_data)
            mchart = (
                alt.Chart(mdf)
                .mark_bar(cornerRadiusEnd=4, size=36)
                .encode(
                    y=alt.Y("type:N", title=None, sort=None,
                            axis=alt.Axis(labelColor="#e5e7eb")),
                    x=alt.X("value:Q", title=None,
                            scale=alt.Scale(domain=[0, 100]),
                            axis=alt.Axis(labelColor="#9ca3af", gridColor="#1f2937")),
                    color=alt.value("#34d399"),
                    tooltip=[alt.Tooltip("type"), alt.Tooltip("value:Q", format=".1f", title="%")],
                )
                .properties(height=200, background="transparent")
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(mchart, use_container_width=True)
        else:
            st.markdown("<div class='body'>Margin data unavailable.</div>", unsafe_allow_html=True)

    with v2:
        st.markdown(
            "<div style='color:#9ca3af;font-size:0.78rem;font-weight:700;"
            "letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;'>"
            "Cash vs Debt</div>",
            unsafe_allow_html=True,
        )
        cd_data = []
        if fins.get("cash") is not None: cd_data.append({"type": "Cash", "value": fins["cash"]})
        if fins.get("total_debt") is not None: cd_data.append({"type": "Debt", "value": fins["total_debt"]})
        if cd_data:
            cdf = pd.DataFrame(cd_data)
            cdchart = (
                alt.Chart(cdf)
                .mark_bar(cornerRadiusEnd=4, size=42)
                .encode(
                    x=alt.X("type:N", title=None, sort=None,
                            axis=alt.Axis(labelColor="#e5e7eb", labelAngle=0)),
                    y=alt.Y("value:Q", title=None,
                            axis=alt.Axis(labelColor="#9ca3af", gridColor="#1f2937")),
                    color=alt.Color("type:N", scale=alt.Scale(
                        domain=["Cash", "Debt"], range=["#34d399", "#f87171"]), legend=None),
                    tooltip=[alt.Tooltip("type"), alt.Tooltip("value:Q", format="$,.0f", title="$M")],
                )
                .properties(height=200, background="transparent")
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(cdchart, use_container_width=True)
        else:
            st.markdown("<div class='body'>Balance sheet data unavailable.</div>", unsafe_allow_html=True)

    with v3:
        st.markdown(
            "<div style='color:#9ca3af;font-size:0.78rem;font-weight:700;"
            "letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;'>"
            "Risk Severity Mix</div>",
            unsafe_allow_html=True,
        )
        if risks:
            sev_counts = {"high": 0, "medium": 0, "low": 0}
            for r in risks:
                sev = (r.get("severity") or "medium").lower()
                if sev in sev_counts: sev_counts[sev] += 1
            rdf = pd.DataFrame([{"severity": k, "count": v} for k, v in sev_counts.items() if v > 0])
            donut = (
                alt.Chart(rdf)
                .mark_arc(innerRadius=50, outerRadius=85)
                .encode(
                    theta=alt.Theta("count:Q"),
                    color=alt.Color("severity:N", scale=alt.Scale(
                        domain=["high", "medium", "low"],
                        range=["#f87171", "#fbbf24", "#34d399"],
                    ), legend=alt.Legend(orient="bottom", labelColor="#e5e7eb", title=None)),
                    tooltip=["severity", "count"],
                )
                .properties(height=200, background="transparent")
                .configure_view(strokeWidth=0)
            )
            st.altair_chart(donut, use_container_width=True)
        else:
            st.markdown("<div class='body'>No risks to chart.</div>", unsafe_allow_html=True)

    # ── Two-column body ────────────────────────────────────────
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown('<div class="section-h">Fundamentals</div>', unsafe_allow_html=True)
        f1, f2 = st.columns(2)
        with f1:
            st.markdown(kpi_card("Revenue (TTM)", fmt_money(fins.get("revenue_ttm"))), unsafe_allow_html=True)
            st.markdown("")
            st.markdown(kpi_card("Free Cash Flow", fmt_money(fins.get("free_cash_flow_ttm"))), unsafe_allow_html=True)
            st.markdown("")
            st.markdown(kpi_card("Operating Margin", fmt_pct(fins.get("operating_margin"))), unsafe_allow_html=True)
        with f2:
            st.markdown(kpi_card("Net Income (TTM)", fmt_money(fins.get("net_income_ttm"))), unsafe_allow_html=True)
            st.markdown("")
            st.markdown(kpi_card("Total Debt", fmt_money(fins.get("total_debt"))), unsafe_allow_html=True)
            st.markdown("")
            st.markdown(kpi_card("Revenue Growth (YoY)", fmt_pct(fins.get("revenue_growth_yoy"))), unsafe_allow_html=True)

        with st.expander("More fundamentals detail"):
            d1, d2 = st.columns(2)
            d1.markdown(
                f"<div class='detail-card'><div class='detail-label'>Market Cap</div>"
                f"<div class='detail-value'>{fmt_money(fins.get('market_cap'))}</div></div>"
                f"<div class='detail-card'><div class='detail-label'>Gross Margin</div>"
                f"<div class='detail-value'>{fmt_pct(fins.get('gross_margin'))}</div></div>",
                unsafe_allow_html=True,
            )
            d2.markdown(
                f"<div class='detail-card'><div class='detail-label'>Cash on Hand</div>"
                f"<div class='detail-value'>{fmt_money(fins.get('cash'))}</div></div>"
                f"<div class='detail-card'><div class='detail-label'>Trailing P/E</div>"
                f"<div class='detail-value'>{fins.get('trailing_pe'):.1f}x" if fins.get('trailing_pe') else "—",
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-h">Valuation Commentary</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="body">{result.get("valuation_notes") or "—"}</div>',
            unsafe_allow_html=True,
        )

        if fins.get("summary"):
            st.markdown('<div class="section-h">Business Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="body">{fins["summary"]}</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-h">Key Risks</div>', unsafe_allow_html=True)
        if risks:
            for i, r in enumerate(risks[:6]):
                sev = (r.get("severity") or "medium").lower()
                if sev not in ("low", "medium", "high"):
                    sev = "medium"
                st.markdown(
                    f'<div class="risk-card">'
                    f'<span class="risk-pill risk-{sev}">{sev}</span>'
                    f'<span class="risk-card-text">{r.get("risk", "")}</span>'
                    f'<div style="color:#9ca3af;font-size:0.72rem;margin-top:6px;">'
                    f'Source: {r.get("source", "—")}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="body">No risks flagged.</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-h">News &amp; Sentiment</div>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="sent sent-{sentiment}">Sentiment: {sentiment}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="body" style="margin-top:10px;">{result.get("news_summary") or "—"}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='color:#9ca3af;font-size:0.78rem;font-weight:700;"
            "letter-spacing:0.1em;text-transform:uppercase;margin:14px 0 8px 0;'>"
            "Recent headlines (click to read)</div>",
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

    # ── Memo + readable raw state ──────────────────────────────
    st.markdown('<div class="section-h">Deep Dive</div>', unsafe_allow_html=True)
    if result.get("memo_markdown"):
        with st.expander("Full investment memo", expanded=False):
            st.markdown(
                f"<div class='memo-box body'>{result['memo_markdown']}</div>",
                unsafe_allow_html=True,
            )

    with st.expander("Agent outputs (structured view)"):
        tabs = st.tabs(["Filings", "News", "Valuation", "Risk", "Editor"])
        with tabs[0]:
            st.markdown('<div class="body">', unsafe_allow_html=True)
            for k, v in (fins or {}).items():
                if v is None: continue
                if isinstance(v, float) and 0 < v < 1:
                    v = f"{v*100:.2f}%"
                elif isinstance(v, (int, float)):
                    v = f"{v:,.2f}"
                st.markdown(
                    f"<div class='detail-card'><div class='detail-label'>{k.replace('_', ' ').title()}</div>"
                    f"<div class='detail-value'>{v}</div></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
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
                    st.markdown(f"<div class='detail-card'><div class='detail-label'>Assumptions</div>"
                                f"<div class='detail-value' style='font-size:0.9rem;'>"
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
                    f'<span class="risk-card-text">{r.get("risk", "")}</span>'
                    f'<div style="color:#9ca3af;font-size:0.72rem;margin-top:6px;">'
                    f'Source: {r.get("source", "—")}</div></div>',
                    unsafe_allow_html=True,
                )
        with tabs[4]:
            st.markdown(f"<div class='body'><b>Recommendation:</b> {rec}<br/><br/>"
                        f"<b>Upside threshold logic:</b><br/>"
                        f"BUY if upside &gt; 15% AND risk ≤ 5<br/>"
                        f"SELL if upside &lt; -10% OR risk ≥ 8<br/>"
                        f"Else HOLD</div>", unsafe_allow_html=True)

    if result.get("errors"):
        with st.expander(f"Agent warnings ({len(result['errors'])})"):
            for e in result["errors"]:
                st.warning(e)

else:
    # ── Empty state ────────────────────────────────────────────
    st.markdown(
        """
        <div style="background:#161b2c;border:1px solid #2a3142;border-radius:14px;
                    padding:48px;text-align:center;margin-top:1rem;">
            <div style="color:#fff;font-size:1.2rem;font-weight:600;margin-bottom:10px;">
                Enter a ticker above to generate a memo
            </div>
            <div style="color:#9ca3af;font-size:0.95rem;">
                Five specialized AI agents will research the company and produce a
                one-page investment memo in roughly 20 seconds.
                <br/><br/>
                Try <b style="color:#fff;">NVDA</b>, <b style="color:#fff;">AAPL</b>,
                <b style="color:#fff;">MSFT</b>, <b style="color:#fff;">TSLA</b>.
            </div>
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
                    1. Filings · fundamentals<br/>
                    2. News · sentiment<br/>
                    3. Valuation · DCF + comps<br/>
                    4. Risk · red flags<br/>
                    5. Editor · final memo
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
            © 2026 Iolanda Costa · LoliFin · For educational purposes only —
            not investment advice.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
