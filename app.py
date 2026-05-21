"""
Streamlit demo UI for lolifin.

Run with: streamlit run app.py
"""
import streamlit as st
from graph import graph

st.set_page_config(page_title="lolifin · Agentic Equity Research", page_icon="📊", layout="wide")

# ── Header ────────────────────────────────────────────────────────────────
st.title("📊 lolifin")
st.subheader("Agentic AI Equity Research Analyst")
st.caption("Multi-agent pipeline → one-page investment memo. Built with LangGraph + Gemini.")

st.markdown(
    """
    <div style="padding: 0.6rem 1rem; background: #f0f4ff; border-left: 4px solid #4b6bfb;
                border-radius: 4px; margin: 0.5rem 0 1.25rem 0; font-size: 0.95rem;">
        <strong>A project by Iolanda Costa</strong> · Master's in Finance & AI,
        Bologna Business School
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
        5 specialized agents run in a graph:
        1. **Filings** — pulls fundamentals
        2. **News** — recent narrative + sentiment
        3. **Valuation** — DCF + comparables
        4. **Risk** — red flag scanner
        5. **Editor** — composes the memo

        **Stack:** Python · LangGraph · Gemini 2.0 Flash ·
        yfinance · SEC EDGAR · Streamlit.
        """
    )
    st.divider()
    st.caption(
        "Built by **Iolanda Costa** as part of her Master's in Finance & AI "
        "at Bologna Business School. For educational purposes only — "
        "not investment advice."
    )

# ── Main interaction ──────────────────────────────────────────────────────
ticker = st.text_input(
    "Ticker", value="NVDA", help="e.g. NVDA, AAPL, MSFT"
).upper().strip()

if st.button("Generate memo", type="primary"):
    if not ticker:
        st.error("Enter a ticker.")
    else:
        with st.spinner(f"Running 5-agent pipeline for {ticker}..."):
            try:
                result = graph.invoke({"ticker": ticker})
                memo = result.get("memo_markdown")
                if memo:
                    st.markdown(memo)
                    with st.expander("Raw agent state (debug)"):
                        st.json(
                            {k: v for k, v in result.items() if k != "memo_markdown"}
                        )
                else:
                    st.error("No memo generated.")
                    if result.get("errors"):
                        for e in result["errors"]:
                            st.warning(e)
            except Exception as e:
                st.error(f"Pipeline failed: {e}")

# ── Footer ────────────────────────────────────────────────────────────────
st.divider()
st.caption("© 2026 Iolanda Costa · Built with LangGraph + Gemini")
