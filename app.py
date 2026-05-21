"""
lolifin — Streamlit dashboard.

Run: streamlit run app.py
"""
import streamlit as st
from graph import graph

st.set_page_config(
    page_title="lolifin · Equity Research",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ───────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* App background */
    .stApp { background: #0e1117; }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }

    /* Top brand bar */
    .brand-bar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 14px 22px; margin: -1rem -1rem 1.5rem -1rem;
        background: linear-gradient(90deg, #0b1437 0%, #1a2b6b 60%, #2541b2 100%);
        border-bottom: 1px solid #2a3a7a;
    }
    .brand-name { color: #fff; font-size: 1.6rem; font-weight: 700; letter-spacing: -0.02em; }
    .brand-tag { color: #9fb4ff; font-size: 0.85rem; font-weight: 500; }
    .brand-credit {
        color: #cfd9ff; font-size: 0.82rem; text-align: right;
        background: rgba(255,255,255,0.06); padding: 6px 12px; border-radius: 6px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .brand-credit b { color: #fff; }

    /* KPI cards */
    .kpi {
        background: #1a1f2e; border: 1px solid #2a3142; border-radius: 10px;
        padding: 16px 18px; height: 100%;
    }
    .kpi-label { color: #8a93a8; font-size: 0.75rem; font-weight: 600;
                 letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
    .kpi-value { color: #ffffff; font-size: 1.55rem; font-weight: 700; line-height: 1.2; }
    .kpi-sub { color: #8a93a8; font-size: 0.78rem; margin-top: 4px; }

    /* Recommendation badge */
    .rec-badge {
        display: inline-block; padding: 8px 20px; border-radius: 6px;
        font-weight: 700; font-size: 1.1rem; letter-spacing: 0.04em;
    }
    .rec-BUY { background: #0f3b2a; color: #34d399; border: 1px solid #34d399; }
    .rec-HOLD { background: #3b2e0f; color: #fbbf24; border: 1px solid #fbbf24; }
    .rec-SELL { background: #3b1212; color: #f87171; border: 1px solid #f87171; }

    /* Section headers */
    .section-h {
        color: #ffffff; font-size: 1.05rem; font-weight: 600;
        margin: 1.5rem 0 0.7rem 0; padding-bottom: 6px;
        border-bottom: 1px solid #2a3142;
    }

    /* Risk pill */
    .risk-pill {
        display: inline-block; padding: 3px 10px; border-radius: 12px;
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.05em;
        text-transform: uppercase; margin-right: 8px;
    }
    .risk-high { background: #3b1212; color: #f87171; }
    .risk-medium { background: #3b2e0f; color: #fbbf24; }
    .risk-low { background: #0f3b2a; color: #34d399; }

    /* Sentiment chip */
    .sent {
        display: inline-block; padding: 4px 12px; border-radius: 14px;
        font-size: 0.78rem; font-weight: 600;
    }
    .sent-positive { background: #0f3b2a; color: #34d399; }
    .sent-neutral { background: #1f2937; color: #9ca3af; }
    .sent-negative { background: #3b1212; color: #f87171; }

    /* Risk-card */
    .risk-card {
        background: #1a1f2e; border: 1px solid #2a3142; border-radius: 8px;
        padding: 12px 14px; margin-bottom: 8px;
    }
    .risk-card-text { color: #cbd5e1; font-size: 0.9rem; }

    /* News card */
    .news-card {
        background: #1a1f2e; border-left: 3px solid #4b6bfb;
        padding: 10px 14px; margin-bottom: 8px; border-radius: 4px;
    }
    .news-card a { color: #cbd5e1; text-decoration: none; font-size: 0.9rem; }
    .news-card a:hover { color: #fff; }
    .news-pub { color: #6b7280; font-size: 0.72rem; margin-top: 2px; }

    /* Body text */
    .body-text { color: #cbd5e1; font-size: 0.95rem; line-height: 1.55; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background: #0a0e17; }
    section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

    /* Input */
    .stTextInput input {
        background: #1a1f2e !important; color: #fff !important;
        border: 1px solid #2a3142 !important; border-radius: 8px !important;
    }

    /* Button */
    .stButton>button {
        background: linear-gradient(90deg, #4b6bfb 0%, #6d8bff 100%);
        color: #fff; border: none; border-radius: 8px; padding: 0.55rem 1.5rem;
        font-weight: 600; letter-spacing: 0.02em;
    }
    .stButton>button:hover { background: linear-gradient(90deg, #3b5beb 0%, #5d7bff 100%); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Brand bar ────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="brand-bar">
        <div>
            <span class="brand-name">lolifin</span>
            <span class="brand-tag">  ·  Agentic Equity Research</span>
        </div>
        <div class="brand-credit">
            A project by <b>Iolanda Costa</b><br>
            <span style="font-size: 0.72rem; color: #9fb4ff;">
                M.Sc. Finance & AI · Bologna Business School
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Pipeline")
    st.markdown(
        """
        <div style="font-size:0.85rem; line-height:1.7;">
        <b>1. Filings</b><br/>
        <span style="color:#8a93a8">Yahoo Finance · fundamentals → JSON</span><br/><br/>
        <b>2. News</b><br/>
        <span style="color:#8a93a8">Headlines → sentiment + narrative</span><br/><br/>
        <b>3. Valuation</b><br/>
        <span style="color:#8a93a8">DCF + comparable multiples</span><br/><br/>
        <b>4. Risk</b><br/>
        <span style="color:#8a93a8">Cross-signal red-flag scan</span><br/><br/>
        <b>5. Editor</b><br/>
        <span style="color:#8a93a8">Composes the final memo</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("### Stack")
    st.markdown(
        "<div style='font-size:0.82rem; color:#8a93a8;'>"
        "Python · LangGraph · Gemini 2.0 Flash · yfinance · SEC EDGAR · Streamlit"
        "</div>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption(
        "Built by **Iolanda Costa** as part of her Master's in Finance & AI at "
        "Bologna Business School. For educational purposes only — not investment advice."
    )


# ── Input row ────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1])
with col_input:
    ticker = st.text_input(
        "Ticker", value="NVDA", label_visibility="collapsed",
        placeholder="Enter ticker (e.g. NVDA, AAPL, MSFT)",
    ).upper().strip()
with col_btn:
    run = st.button("Generate", type="primary", use_container_width=True)


# ── Helpers ──────────────────────────────────────────────────────────────
def kpi(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{sub_html}</div>'


def fmt_money(v, suffix=""):
    if v is None:
        return "—"
    if isinstance(v, (int, float)):
        if abs(v) >= 1000:
            return f"${v/1000:.1f}B{suffix}"
        return f"${v:,.0f}M{suffix}"
    return str(v)


def fmt_pct(v):
    if v is None:
        return "—"
    return f"{v*100:.1f}%" if abs(v) < 5 else f"{v:.1f}%"


# ── Render results ──────────────────────────────────────────────────────
if run:
    if not ticker:
        st.error("Enter a ticker.")
    else:
        with st.spinner(f"Running 5-agent pipeline for {ticker}..."):
            try:
                result = graph.invoke({"ticker": ticker})
            except Exception as e:
                st.error(f"Pipeline failed: {e}")
                st.stop()

        company = result.get("company_name") or ticker
        rec = result.get("recommendation") or "HOLD"
        val = result.get("valuation") or {}
        fins = result.get("financials") or {}
        risks = result.get("risks") or []
        risk_score = result.get("risk_score")
        sentiment = (result.get("news_sentiment") or "neutral").lower()

        # ── Headline row ───────────────────────────────────────────
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.markdown(
                f"<h2 style='color:#fff;margin-bottom:0;'>{company} "
                f"<span style='color:#8a93a8;font-size:1.1rem;font-weight:500;'>({ticker})</span></h2>",
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f"<div style='text-align:right;margin-top:6px;'>"
                f"<span class='rec-badge rec-{rec}'>{rec}</span></div>",
                unsafe_allow_html=True,
            )

        # ── KPI tiles ──────────────────────────────────────────────
        upside = val.get("upside_pct")
        upside_str = f"{upside:+.1f}%" if upside is not None else "—"
        upside_color = "#34d399" if (upside or 0) > 0 else ("#f87171" if (upside or 0) < 0 else "#9ca3af")

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(kpi("Current Price",
                        f"${val.get('current_price'):.2f}" if val.get('current_price') else "—"),
                    unsafe_allow_html=True)
        c2.markdown(kpi("Fair Value (blended)",
                        f"${val.get('blended_fair_value'):.2f}" if val.get('blended_fair_value') else "—",
                        f"DCF ${val.get('dcf_fair_value')} · Comps ${val.get('comp_fair_value')}"
                        if val.get('dcf_fair_value') and val.get('comp_fair_value') else ""),
                    unsafe_allow_html=True)
        c3.markdown(
            f'<div class="kpi"><div class="kpi-label">Upside</div>'
            f'<div class="kpi-value" style="color:{upside_color};">{upside_str}</div></div>',
            unsafe_allow_html=True,
        )
        risk_display = f"{risk_score}/10" if risk_score else "—"
        risk_sub = "low risk" if (risk_score or 0) <= 4 else ("elevated" if (risk_score or 0) >= 7 else "moderate")
        c4.markdown(kpi("Risk Score", risk_display, risk_sub), unsafe_allow_html=True)

        # ── Two-column main body ───────────────────────────────────
        st.markdown('<div class="section-h">Investment Thesis</div>', unsafe_allow_html=True)
        memo = result.get("memo_markdown") or ""
        # Strip the H1 header that the editor adds (we already show it above)
        thesis_section = memo.split("## Thesis", 1)
        if len(thesis_section) > 1:
            thesis_body = thesis_section[1].split("##", 1)[0].strip()
            st.markdown(f'<div class="body-text">{thesis_body}</div>', unsafe_allow_html=True)

        left, right = st.columns([1.2, 1])

        with left:
            st.markdown('<div class="section-h">Fundamentals</div>', unsafe_allow_html=True)
            f1, f2 = st.columns(2)
            with f1:
                st.markdown(kpi("Revenue (TTM)", fmt_money(fins.get("revenue_ttm"))), unsafe_allow_html=True)
                st.markdown("")
                st.markdown(kpi("Free Cash Flow", fmt_money(fins.get("free_cash_flow_ttm"))), unsafe_allow_html=True)
                st.markdown("")
                st.markdown(kpi("Operating Margin", fmt_pct(fins.get("operating_margin"))), unsafe_allow_html=True)
            with f2:
                st.markdown(kpi("Net Income (TTM)", fmt_money(fins.get("net_income_ttm"))), unsafe_allow_html=True)
                st.markdown("")
                st.markdown(kpi("Total Debt", fmt_money(fins.get("total_debt"))), unsafe_allow_html=True)
                st.markdown("")
                st.markdown(kpi("Revenue Growth (YoY)", fmt_pct(fins.get("revenue_growth_yoy"))), unsafe_allow_html=True)

            st.markdown('<div class="section-h">Valuation Commentary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="body-text">{result.get("valuation_notes") or "—"}</div>',
                        unsafe_allow_html=True)

        with right:
            st.markdown('<div class="section-h">Key Risks</div>', unsafe_allow_html=True)
            if risks:
                for r in risks[:5]:
                    sev = (r.get("severity") or "medium").lower()
                    st.markdown(
                        f'<div class="risk-card">'
                        f'<span class="risk-pill risk-{sev}">{sev}</span>'
                        f'<span class="risk-card-text">{r.get("risk", "")}</span>'
                        f'<div style="color:#6b7280;font-size:0.72rem;margin-top:4px;">'
                        f'source: {r.get("source", "—")}</div></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<div class="body-text">No risks flagged.</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-h">News &amp; Sentiment</div>', unsafe_allow_html=True)
            st.markdown(
                f'<span class="sent sent-{sentiment}">Sentiment: {sentiment}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="body-text" style="margin-top:10px;">{result.get("news_summary") or "—"}</div>',
                unsafe_allow_html=True,
            )
            sources = result.get("news_sources") or []
            if sources:
                st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)
                for s in sources[:4]:
                    title = s.get("title", "")
                    url = s.get("url") or "#"
                    pub = s.get("publisher") or ""
                    st.markdown(
                        f'<div class="news-card"><a href="{url}" target="_blank">{title}</a>'
                        f'<div class="news-pub">{pub}</div></div>',
                        unsafe_allow_html=True,
                    )

        # ── Full memo expander ────────────────────────────────────
        with st.expander("Full memo (markdown)"):
            st.markdown(memo)

        with st.expander("Raw agent state (debug)"):
            st.json({k: v for k, v in result.items() if k != "memo_markdown"})

        if result.get("errors"):
            with st.expander("Agent warnings"):
                for e in result["errors"]:
                    st.warning(e)

else:
    # Empty state
    st.markdown(
        """
        <div style="background:#1a1f2e;border:1px solid #2a3142;border-radius:12px;
                    padding:40px;text-align:center;margin-top:1rem;">
            <div style="color:#fff;font-size:1.15rem;font-weight:600;margin-bottom:6px;">
                Enter a ticker above to generate a memo
            </div>
            <div style="color:#8a93a8;font-size:0.9rem;">
                Five AI agents will research the company and produce a one-page
                investment memo in ~20 seconds.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Footer ───────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:#6b7280;font-size:0.78rem;padding:1rem 0;'>"
    "© 2026 Iolanda Costa · lolifin · Built with LangGraph + Gemini"
    "</div>",
    unsafe_allow_html=True,
)
