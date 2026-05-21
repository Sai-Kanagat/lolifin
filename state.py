"""
Shared state passed between agents in the LangGraph pipeline.

Each agent reads from this dict and writes its results back. This is the
"shared memory" that makes the system *agentic* rather than a single prompt.

Note on `errors`: it uses `Annotated[list, operator.add]` so that when
parallel agents (news + valuation) both append to it, LangGraph concatenates
the lists instead of complaining about concurrent writes. Every other key is
written by exactly one agent, so no reducer needed.
"""
import operator
from typing import TypedDict, Optional, Annotated


class ResearchState(TypedDict, total=False):
    # Input
    ticker: str

    # Filings agent output
    company_name: Optional[str]
    financials: Optional[dict]
    filing_url: Optional[str]
    filing_date: Optional[str]

    # News agent output
    news_summary: Optional[str]
    news_sentiment: Optional[str]
    news_sources: Optional[list]

    # Valuation agent output
    valuation: Optional[dict]
    valuation_notes: Optional[str]

    # Risk agent output
    risks: Optional[list]
    risk_score: Optional[int]

    # Editor agent output
    memo_markdown: Optional[str]
    recommendation: Optional[str]

    # Error tracking — additive across parallel branches
    errors: Annotated[list, operator.add]
