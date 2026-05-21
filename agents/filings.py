"""
Filings Agent
-------------
Pulls fundamental financial data directly from Yahoo Finance and normalizes
into a clean structure. The LLM is used ONLY for the optional narrative
summary — the numbers themselves are deterministic so the dashboard never
shows blank tiles when the LLM has a bad day.

Also pulls 6 months of price history so the app can render a chart.
"""
import yfinance as yf
from langchain_core.messages import HumanMessage, SystemMessage

from llm import get_llm
from state import ResearchState


def _to_millions(v):
    """Convert raw yfinance value (in dollars) to millions, or None."""
    if v is None or not isinstance(v, (int, float)):
        return None
    return round(v / 1_000_000, 1)


def filings_agent(state: ResearchState) -> ResearchState:
    ticker = state["ticker"]

    try:
        tk = yf.Ticker(ticker)
        info = tk.info or {}

        # Deterministic extraction — never returns None for the whole block
        financials = {
            "company_name": info.get("longName") or info.get("shortName") or ticker,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "revenue_ttm": _to_millions(info.get("totalRevenue")),
            "net_income_ttm": _to_millions(info.get("netIncomeToCommon")),
            "free_cash_flow_ttm": _to_millions(info.get("freeCashflow")),
            "total_debt": _to_millions(info.get("totalDebt")),
            "cash": _to_millions(info.get("totalCash")),
            "gross_margin": info.get("grossMargins"),
            "operating_margin": info.get("operatingMargins"),
            "revenue_growth_yoy": info.get("revenueGrowth"),
            "market_cap": _to_millions(info.get("marketCap")),
            "trailing_pe": info.get("trailingPE"),
        }

        # Price history for chart (6 months daily close)
        price_history = []
        try:
            hist = tk.history(period="6mo")
            if not hist.empty:
                price_history = [
                    {"date": d.strftime("%Y-%m-%d"), "close": round(float(c), 2)}
                    for d, c in hist["Close"].items()
                ]
        except Exception:
            pass

        # Optional LLM summary — if it fails, we still have all the numbers
        summary = None
        try:
            llm = get_llm(temperature=0.2)
            biz = (info.get("longBusinessSummary") or "")[:1200]
            resp = llm.invoke([
                SystemMessage(content="Write a 2-3 sentence summary of this company's financial health. Plain prose, no JSON, no markdown."),
                HumanMessage(content=f"Company: {financials['company_name']}\nFinancials: {financials}\nBusiness: {biz}"),
            ])
            summary = resp.content.strip()
        except Exception:
            # No noisy fallback — just leave blank; the numbers speak.
            summary = ""

        financials["summary"] = summary

        return {
            "company_name": financials["company_name"],
            "financials": financials,
            "filing_url": f"https://finance.yahoo.com/quote/{ticker}",
            "filing_date": str(info.get("mostRecentQuarter") or ""),
            "price_history": price_history,
            "errors": [],
        }
    except Exception as e:
        return {"errors": [f"filings_agent: {e}"], "financials": None, "price_history": []}
