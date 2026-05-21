# LoliFin · Agentic AI Equity Research Analyst

A multi-agent pipeline that takes a stock ticker and produces a one-page investment memo (Buy / Hold / Sell, with reasoning, valuation, risks, and citations).

> **A project by Iolanda Costa** — Master's in Finance & AI, Bologna Business School.

## What it does

Input: `NVDA`
Output: A research memo with thesis, fundamentals, DCF + comps valuation, recent news sentiment, top risks, and a recommendation — generated in ~20 seconds by 5 specialized AI agents working together.

## Architecture

```
                   User: ticker
                        │
                ┌───────▼────────┐
                │  Orchestrator   │  (LangGraph state machine)
                └───────┬────────┘
                        │
                ┌───────▼────────┐
                │  Filings Agent │  ← pulls fundamentals (yfinance)
                └───────┬────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
     ┌───────────────┐   ┌────────────────┐
     │  News Agent   │   │ Valuation Agent│
     │  (yfinance    │   │  (DCF + comps) │
     │  news + LLM)  │   │                │
     └───────┬───────┘   └────────┬───────┘
             │                    │
             └─────────┬──────────┘
                       ▼
              ┌────────────────┐
              │  Risk Agent    │  ← cross-references everything
              └────────┬───────┘
                       ▼
              ┌────────────────┐
              │  Editor Agent  │  ← composes the memo
              └────────┬───────┘
                       ▼
                 memo.md
```

## Tech stack

- **Python 3.11**
- **LangGraph** — agent orchestration via state graph
- **Gemini 2.0 Flash** — LLM (free tier, no credit card needed)
- **yfinance** — market data + news (free, no key)
- **SEC EDGAR** — filings (free, no key)
- **Streamlit** — demo UI

## Setup

```bash
# 1. Clone + install
pip install -r requirements.txt

# 2. Get a free Gemini API key at https://aistudio.google.com/app/apikey
cp .env.example .env
# Then edit .env and paste your key

# 3. Run
python run.py NVDA --save        # CLI
streamlit run app.py             # UI
```

## Sample output

See `sample_memos/` for pre-generated memos on NVDA, LVMH, and ENI.

## Why agentic (not just one prompt)?

- **Specialization** — each agent has one job, one system prompt, one schema.
- **Determinism where it matters** — DCF math is Python, not LLM.
- **Cross-agent reasoning** — the risk agent reads outputs from filings + news + valuation and synthesizes.
- **Extensibility** — adding a "compliance check" or "peer review" agent is one node, not a rewrite.

## Project structure

```
03-agentic-research/
├── agents/
│   ├── filings.py       # Fundamentals extraction
│   ├── news.py          # News sentiment + summary
│   ├── valuation.py     # DCF + comparable multiples
│   ├── risk.py          # Red flag scanner
│   └── editor.py        # Memo composition
├── state.py             # Shared state schema (TypedDict)
├── llm.py               # Gemini client config
├── graph.py             # LangGraph orchestrator
├── run.py               # CLI entry point
├── app.py               # Streamlit demo
└── sample_memos/        # Pre-generated examples
```

## License

MIT — feel free to fork, extend, learn from.
