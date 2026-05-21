"""
Shared state passed between agents in the LangGraph pipeline.

Each agent reads from this dict and writes its results back. This is the
"shared memory" that makes the system *agentic* rather than a single prompt.
"""
from typing import TypedDict, Optional


class ResearchState(TypedDict, total=False):
    # Input
    ticker: str

    # Filings agent output
    company_name: Optional[str]
    financials: Optional[dict]   # revenue, net_income, fcf, debt, margins, etc.
    filing_url: Optional[str]
    filing_date: Optional[str]

    # News agent output
    news_summary: Optional[str]
    news_sentiment: Optional[str]   # "positive" | "neutral" | "negative"
    news_sources: Optional[list]    # list of {title, url, date}

    # Valuation agent output
    valuation: Optional[dict]       # {dcf_fair_value, comp_fair_value, current_price, upside_pct}
    valuation_notes: Optional[str]

    # Risk agent output
    risks: Optional[list]           # list of {risk, severity, source}
    risk_score: Optional[int]       # 1-10

    # Editor agent output
    memo_markdown: Optional[str]
    recommendation: Optional[str]   # "BUY" | "HOLD" | "SELL"

    # Error tracking
    errors: Optional[list]
