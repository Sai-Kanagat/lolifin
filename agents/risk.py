"""
Risk Agent
----------
Scans the filings + news context for red flags. Outputs a structured risk
list and an overall 1-10 score.

This agent demonstrates *cross-agent reasoning*: it uses outputs from both
filings_agent and news_agent — none of which it pulled itself. That's a
core agentic-system property (shared state, downstream consumption).
"""
import json
from langchain_core.messages import HumanMessage, SystemMessage

from llm import get_llm
from state import ResearchState


SYSTEM = """You are a credit/risk analyst. Identify red flags from the data given.
Return ONLY JSON:
{
  "risks": [
    {"risk": "short description", "severity": "low|medium|high", "source": "filings|news|valuation"}
  ],
  "overall_score": 1-10 (1 = very safe, 10 = avoid)
}

Look for: declining margins, leverage, negative FCF, slowing growth, regulatory news,
management changes, accounting concerns, customer concentration, macro exposure.

Always return at least 3 risks. Be honest, not alarmist.
"""


def risk_agent(state: ResearchState) -> ResearchState:
    errors = state.get("errors") or []

    try:
        context = {
            "ticker": state.get("ticker"),
            "company": state.get("company_name"),
            "financials": state.get("financials"),
            "news_summary": state.get("news_summary"),
            "news_sentiment": state.get("news_sentiment"),
            "valuation": state.get("valuation"),
        }

        llm = get_llm(temperature=0.2)
        resp = llm.invoke([
            SystemMessage(content=SYSTEM),
            HumanMessage(content=f"Analyze this company:\n```json\n{json.dumps(context, default=str)}\n```\n\nReturn JSON."),
        ])

        text = resp.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        parsed = json.loads(text)

        return {
            "risks": parsed.get("risks", []),
            "risk_score": parsed.get("overall_score"),
            "errors": errors,
        }
    except Exception as e:
        errors.append(f"risk_agent: {e}")
        return {"risks": [], "risk_score": None, "errors": errors}
