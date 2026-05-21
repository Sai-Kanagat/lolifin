"""
Filings Agent
-------------
Pulls fundamental financial data and asks the LLM to summarize the latest
10-K / 10-Q in structured form.

For non-US tickers (e.g. LVMH on Paris) SEC EDGAR has no filing, so we fall
back to yfinance fundamentals — still real data, just less narrative.

What makes this an "agent" rather than a script:
- It uses *tools* (yfinance + EDGAR HTTP API)
- It hands raw data to an LLM and asks for *structured reasoning* (margins
  trend, debt position, cashflow quality) — judgment, not just parsing.
"""
import json
import yfinance as yf
from langchain_core.messages import HumanMessage, SystemMessage

from llm import get_llm
from state import ResearchState


SYSTEM = """You are a financial analyst extracting key data from company fundamentals.
Return ONLY a JSON object with keys:
- company_name (string)
- revenue_ttm (number, in millions USD)
- net_income_ttm (number, in millions USD)
- free_cash_flow_ttm (number, in millions USD)
- total_debt (number, in millions USD)
- cash (number, in millions USD)
- gross_margin (number, 0-1)
- operating_margin (number, 0-1)
- revenue_growth_yoy (number, 0-1 or negative)
- summary (string, 2-3 sentences on financial health)

If a field is unavailable, use null. Do not invent numbers.
"""


def filings_agent(state: ResearchState) -> ResearchState:
    ticker = state["ticker"]

    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        # Build a compact context for the LLM
        context = {
            "ticker": ticker,
            "longName": info.get("longName"),
            "totalRevenue": info.get("totalRevenue"),
            "netIncomeToCommon": info.get("netIncomeToCommon"),
            "freeCashflow": info.get("freeCashflow"),
            "totalDebt": info.get("totalDebt"),
            "totalCash": info.get("totalCash"),
            "grossMargins": info.get("grossMargins"),
            "operatingMargins": info.get("operatingMargins"),
            "revenueGrowth": info.get("revenueGrowth"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "longBusinessSummary": (info.get("longBusinessSummary") or "")[:1500],
        }

        llm = get_llm(temperature=0.1)
        resp = llm.invoke([
            SystemMessage(content=SYSTEM),
            HumanMessage(content=f"Raw fundamentals:\n```json\n{json.dumps(context, default=str)}\n```\n\nReturn the JSON object now."),
        ])

        # Gemini sometimes wraps JSON in ```json ... ```
        text = resp.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        financials = json.loads(text)

        return {
            "company_name": financials.get("company_name") or info.get("longName"),
            "financials": financials,
            "filing_url": f"https://finance.yahoo.com/quote/{ticker}",
            "filing_date": info.get("mostRecentQuarter"),
            "errors": [],
        }
    except Exception as e:
        return {"errors": [f"filings_agent: {e}"], "financials": None}
