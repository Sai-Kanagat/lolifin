"""
News Agent
----------
Pulls recent headlines from Yahoo Finance (via yfinance, no key) and asks the
LLM to summarize the dominant narratives and overall sentiment.

Why we don't use a paid news API: Yahoo's news feed is good enough for
30-day equity coverage on most large/mid-caps, and keeping the project
zero-cost is a hard requirement.
"""
import json
import yfinance as yf
from langchain_core.messages import HumanMessage, SystemMessage

from llm import get_llm
from state import ResearchState


SYSTEM = """You are a financial news analyst. Given recent headlines about a company,
return ONLY a JSON object with:
- sentiment: one of "positive", "neutral", "negative"
- top_narratives: array of 3 short bullet strings describing what's driving the story
- summary: 2-3 sentence summary of the recent news flow

Be evidence-based. If headlines are mixed, say neutral.
"""


def news_agent(state: ResearchState) -> ResearchState:
    ticker = state["ticker"]
    errors = state.get("errors") or []

    try:
        tk = yf.Ticker(ticker)
        raw_news = tk.news or []

        # yfinance news shape varies; normalize to title + publisher + link
        items = []
        for n in raw_news[:15]:
            content = n.get("content") or n
            title = content.get("title") or n.get("title")
            link = content.get("canonicalUrl", {}).get("url") if isinstance(content.get("canonicalUrl"), dict) else n.get("link")
            publisher = content.get("provider", {}).get("displayName") if isinstance(content.get("provider"), dict) else n.get("publisher")
            if title:
                items.append({"title": title, "publisher": publisher, "url": link})

        if not items:
            return {**state, "news_summary": "No recent news available.", "news_sentiment": "neutral", "news_sources": []}

        headlines_text = "\n".join(f"- {it['title']} ({it.get('publisher', 'unknown')})" for it in items)

        llm = get_llm(temperature=0.2)
        resp = llm.invoke([
            SystemMessage(content=SYSTEM),
            HumanMessage(content=f"Ticker: {ticker}\n\nRecent headlines:\n{headlines_text}\n\nReturn JSON."),
        ])

        text = resp.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        parsed = json.loads(text)

        return {
            **state,
            "news_summary": parsed.get("summary"),
            "news_sentiment": parsed.get("sentiment"),
            "news_sources": items[:5],
            "errors": errors,
        }
    except Exception as e:
        errors.append(f"news_agent: {e}")
        return {**state, "news_summary": None, "news_sentiment": "neutral", "news_sources": [], "errors": errors}
