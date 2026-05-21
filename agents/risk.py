"""
Risk Agent
----------
Cross-references filings + news + valuation outputs and extracts risk flags.
"""
import json
import re
from langchain_core.messages import HumanMessage, SystemMessage

from llm import get_llm
from state import ResearchState


def _extract_json(text: str):
    m = re.search(r"\{.*\}", text.strip(), re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


SYSTEM = (
    "You are a credit and equity risk analyst. From the data provided, identify "
    "the top risks. Respond with a single JSON object (no markdown, no preamble) "
    "with keys: "
    'risks (array of objects each with "risk" (short description), '
    '"severity" (one of "low","medium","high"), and "source" (one of '
    '"filings","news","valuation","macro")), '
    "and overall_score (integer 1-10 where 1=very safe, 10=avoid). "
    "Always return at least 3 risks. Be evidence-based, not alarmist."
)


def _fallback_risks(state: ResearchState):
    """Deterministic fallback when the LLM is unavailable."""
    risks = []
    fins = state.get("financials") or {}
    val = state.get("valuation") or {}

    if fins.get("revenue_growth_yoy") is not None and fins["revenue_growth_yoy"] < 0:
        risks.append({"risk": "Revenue declining year-over-year", "severity": "high", "source": "filings"})
    if fins.get("operating_margin") is not None and fins["operating_margin"] < 0.05:
        risks.append({"risk": "Thin or negative operating margins", "severity": "high", "source": "filings"})
    if fins.get("free_cash_flow_ttm") is not None and fins["free_cash_flow_ttm"] < 0:
        risks.append({"risk": "Negative free cash flow", "severity": "high", "source": "filings"})
    if fins.get("total_debt") and fins.get("cash") and fins["total_debt"] > 3 * (fins["cash"] or 1):
        risks.append({"risk": "Debt materially exceeds cash on balance sheet", "severity": "medium", "source": "filings"})
    if val.get("upside_pct") is not None and val["upside_pct"] < -10:
        risks.append({"risk": "Stock trades meaningfully above blended fair value", "severity": "medium", "source": "valuation"})
    if state.get("news_sentiment") == "negative":
        risks.append({"risk": "Negative recent news sentiment", "severity": "medium", "source": "news"})

    if not risks:
        risks = [
            {"risk": "General market and macroeconomic exposure", "severity": "medium", "source": "macro"},
            {"risk": "Sector-specific cyclicality", "severity": "medium", "source": "macro"},
            {"risk": "Execution and management risk inherent to any equity", "severity": "low", "source": "macro"},
        ]

    return risks, 5


def risk_agent(state: ResearchState) -> ResearchState:
    try:
        context = {
            "ticker": state.get("ticker"),
            "company": state.get("company_name"),
            "financials": state.get("financials"),
            "news_summary": state.get("news_summary"),
            "news_sentiment": state.get("news_sentiment"),
            "valuation": state.get("valuation"),
        }

        try:
            llm = get_llm(temperature=0.2)
            resp = llm.invoke([
                SystemMessage(content=SYSTEM),
                HumanMessage(content=f"Data:\n```json\n{json.dumps(context, default=str)}\n```"),
            ])
            parsed = _extract_json(resp.content)
            if parsed and parsed.get("risks"):
                return {
                    "risks": parsed.get("risks", []),
                    "risk_score": parsed.get("overall_score") or 5,
                    "errors": [],
                }
        except Exception:
            pass

        # Fallback if LLM failed or returned junk
        risks, score = _fallback_risks(state)
        return {"risks": risks, "risk_score": score, "errors": []}

    except Exception as e:
        risks, score = _fallback_risks(state)
        return {"risks": risks, "risk_score": score, "errors": [f"risk_agent: {e}"]}
