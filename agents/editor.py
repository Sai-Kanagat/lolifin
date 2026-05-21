"""
Editor Agent
------------
Composes the final one-page investment memo. Reads everything in the shared
state, decides Buy/Hold/Sell, writes prose with citations.

Why a separate agent: separation of concerns. Earlier agents do research;
this one does *synthesis*. In real research desks the analyst writing the
note isn't the one pulling the data — same logic here.
"""
import json
from langchain_core.messages import HumanMessage, SystemMessage

from llm import get_llm
from state import ResearchState


SYSTEM = """You are the lead author of a one-page equity research memo.

Structure:
# {Company} ({Ticker}) — {BUY|HOLD|SELL}

**Current Price:** $X | **Fair Value:** $Y | **Upside:** Z%

## Thesis
2-3 sentence investment thesis.

## Fundamentals
3-4 bullet points on financial health, citing the filings data.

## Valuation
2-3 sentences on what the model says. Reference DCF and comps explicitly.

## News & Sentiment
2 sentences on recent narrative. Sentiment label.

## Key Risks
Top 3 risks as bullets, with severity tag.

## Recommendation
1-2 sentences justifying the BUY/HOLD/SELL call based on upside vs risk.

Rules:
- Every claim must be backed by data in the context. Never invent numbers.
- BUY if blended upside > 15% and risk_score <= 5
- SELL if blended upside < -10% OR risk_score >= 8
- HOLD otherwise
- Output clean Markdown only. No preamble.
"""


def editor_agent(state: ResearchState) -> ResearchState:
    errors = state.get("errors") or []

    context = {
        "ticker": state.get("ticker"),
        "company_name": state.get("company_name"),
        "financials": state.get("financials"),
        "valuation": state.get("valuation"),
        "valuation_notes": state.get("valuation_notes"),
        "news_summary": state.get("news_summary"),
        "news_sentiment": state.get("news_sentiment"),
        "news_sources": state.get("news_sources"),
        "risks": state.get("risks"),
        "risk_score": state.get("risk_score"),
    }

    # Deterministic recommendation logic (don't trust LLM to follow rules perfectly)
    upside = (state.get("valuation") or {}).get("upside_pct")
    risk_score = state.get("risk_score") or 5
    if upside is not None and upside > 15 and risk_score <= 5:
        rec = "BUY"
    elif upside is not None and (upside < -10 or risk_score >= 8):
        rec = "SELL"
    else:
        rec = "HOLD"

    try:
        llm = get_llm(temperature=0.4)
        resp = llm.invoke([
            SystemMessage(content=SYSTEM),
            HumanMessage(content=f"The recommendation is: {rec}\n\nContext:\n```json\n{json.dumps(context, default=str)}\n```\n\nWrite the memo."),
        ])

        return {"memo_markdown": resp.content.strip(), "recommendation": rec, "errors": errors}
    except Exception as e:
        errors.append(f"editor_agent: {e}")
        return {"memo_markdown": None, "recommendation": rec, "errors": errors}
