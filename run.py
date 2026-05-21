"""
CLI entry point.

Usage:
    python run.py NVDA
    python run.py AAPL --save
"""
import sys
import argparse
from pathlib import Path

from graph import graph


def main():
    parser = argparse.ArgumentParser(description="Agentic AI Equity Research Analyst")
    parser.add_argument("ticker", help="Stock ticker (e.g. NVDA, AAPL)")
    parser.add_argument("--save", action="store_true", help="Save memo to sample_memos/")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    print(f"\nResearching {ticker}...\n")

    result = graph.invoke({"ticker": ticker})

    memo = result.get("memo_markdown") or "(no memo generated)"
    print("=" * 70)
    print(memo)
    print("=" * 70)

    if result.get("errors"):
        print("\nAgent errors:")
        for e in result["errors"]:
            print(f"  - {e}")

    if args.save:
        out = Path(__file__).parent / "sample_memos" / f"{ticker}.md"
        out.write_text(memo, encoding="utf-8")
        print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
