"""
News Agent
----------
Pulls recent headlines from Yahoo Finance (via yfinance, no key) and asks the
LLM to label sentiment. Sources are always returned even if the LLM fails.
"""
import json
import re
import yfinance as yf
from langchain_core.messages import HumanMessage, SystemMessage

from llm import get_llm
from state import ResearchState


def _extract_json(text: str):
    """Pull a JSON object out of an LLM response, even if wrapped in markdown."""
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


SYSTEM = (
    "You are a financial news analyst. Given recent headlines about a company, "
    "respond with a single JSON object — no markdown, no preamble — with keys: "
    'sentiment (one of "positive", "neutral", "negative"), '
    "top_narratives (array of 3 short bullet strings), "
    "summary (2-3 sentence summary)."
)


def news_agent(state: ResearchState) -> ResearchState:
    ticker = state["ticker"]

    try:
        tk = yf.Ticker(ticker)
        raw_news = tk.news or []

        items = []
        for n in raw_news[:15]:
            content = n.get("content") or n
            title = content.get("title") or n.get("title")
            cu = content.get("canonicalUrl")
            link = (cu.get("url") if isinstance(cu, dict) else None) or n.get("link")
            prov = content.get("provider")
            publisher = (prov.get("displayName") if isinstance(prov, dict) else None) or n.get("publisher")
            if title:
                items.append({"title": title, "publisher": publisher, "url": link})

        if not items:
            return {
                "news_summary": "No recent news available for this ticker.",
                "news_sentiment": "neutral",
                "news_sources": [],
                "errors": [],
            }

        headlines = "\n".join(f"- {it['title']} ({it.get('publisher') or 'unknown'})" for it in items)

        # LLM is best-effort. If parsing fails we still return the headlines.
        try:
            llm = get_llm(temperature=0.2)
            resp = llm.invoke([
                SystemMessage(content=SYSTEM),
                HumanMessage(content=f"Ticker: {ticker}\n\nHeadlines:\n{headlines}"),
            ])
            parsed = _extract_json(resp.content) or {}
            sentiment = parsed.get("sentiment") or "neutral"
            summary = parsed.get("summary") or "Recent headlines summarized below."
        except Exception:
            sentiment = "neutral"
            summary = "Recent headlines summarized below (LLM unavailable)."

        return {
            "news_summary": summary,
            "news_sentiment": sentiment,
            "news_sources": items[:6],
            "errors": [],
        }
    except Exception as e:
        return {
            "news_summary": "News pull failed.",
            "news_sentiment": "neutral",
            "news_sources": [],
            "errors": [f"news_agent: {e}"],
        }
