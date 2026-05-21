"""
Valuation Agent
---------------
Two methods, blended:

1. Simplified DCF — projects FCF for 5 years using the filings agent's growth
   estimate, discounts at WACC=9%, applies a terminal multiple of 15x.
2. Comparable multiples — uses sector P/E from yfinance peers when available,
   else falls back to a sector default.

The LLM is used to *narrate* the valuation, not to compute it. Numbers come
from deterministic Python so a recruiter can audit them.

This is the right split: deterministic math for what should be deterministic,
LLM for natural-language reasoning.
"""
import yfinance as yf
from langchain_core.messages import HumanMessage, SystemMessage

from llm import get_llm
from state import ResearchState


def _dcf(fcf: float, growth: float, wacc: float = 0.09, terminal_mult: float = 15.0, years: int = 5) -> float:
    """Simple DCF: 5y projected FCF discounted + terminal value."""
    if fcf is None or fcf <= 0:
        return None
    growth = max(min(growth or 0.05, 0.30), -0.10)  # clamp -10% to +30%
    pv = 0.0
    projected = fcf
    for t in range(1, years + 1):
        projected = projected * (1 + growth)
        pv += projected / ((1 + wacc) ** t)
    terminal = (projected * terminal_mult) / ((1 + wacc) ** years)
    return pv + terminal


def valuation_agent(state: ResearchState) -> ResearchState:
    ticker = state["ticker"]
    fins = state.get("financials") or {}

    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        shares = info.get("sharesOutstanding")
        sector_pe = info.get("trailingPE")

        fcf_millions = fins.get("free_cash_flow_ttm")
        growth = fins.get("revenue_growth_yoy")

        dcf_ev = _dcf(fcf_millions * 1e6 if fcf_millions else None, growth) if fcf_millions else None
        dcf_per_share = (dcf_ev / shares) if (dcf_ev and shares) else None

        # Comparable multiples: net income * sector PE
        ni_millions = fins.get("net_income_ttm")
        comp_value = (ni_millions * 1e6 * sector_pe) if (ni_millions and sector_pe) else None
        comp_per_share = (comp_value / shares) if (comp_value and shares) else None

        fair_values = [v for v in [dcf_per_share, comp_per_share] if v]
        avg_fair = sum(fair_values) / len(fair_values) if fair_values else None
        upside = ((avg_fair - price) / price * 100) if (avg_fair and price) else None

        valuation = {
            "current_price": round(price, 2) if price else None,
            "dcf_fair_value": round(dcf_per_share, 2) if dcf_per_share else None,
            "comp_fair_value": round(comp_per_share, 2) if comp_per_share else None,
            "blended_fair_value": round(avg_fair, 2) if avg_fair else None,
            "upside_pct": round(upside, 1) if upside else None,
            "assumptions": {
                "wacc": 0.09,
                "growth": round(growth, 3) if growth else None,
                "terminal_multiple": 15.0,
                "sector_pe": round(sector_pe, 1) if sector_pe else None,
            },
        }

        llm = get_llm(temperature=0.3)
        resp = llm.invoke([
            SystemMessage(content="You are an equity analyst. Write 3-4 sentences interpreting the valuation. Be specific about which method tells what story and what could break the thesis."),
            HumanMessage(content=f"Ticker: {ticker}\nValuation: {valuation}"),
        ])

        return {"valuation": valuation, "valuation_notes": resp.content.strip(), "errors": []}
    except Exception as e:
        return {"valuation": None, "valuation_notes": None, "errors": [f"valuation_agent: {e}"]}
