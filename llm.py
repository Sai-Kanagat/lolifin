"""
LLM client config. Uses Gemini 2.5 Flash Lite (free tier).

Why Flash Lite over Flash:
- Free tier: ~1,000 requests/day on Lite vs 20/day on regular Flash.
- Quality is essentially the same for short structured tasks.
- For long-form (memo prose) we still get fluent output.

Includes a single retry on 429 (rate limit) with a brief delay.
"""
import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def _get_api_key():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GOOGLE_API_KEY")
        except Exception:
            pass
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY not set. Get a free key at "
            "https://aistudio.google.com/app/apikey and add it to .env "
            "or to Streamlit secrets when deploying."
        )
    return api_key


class _RetryingChat:
    """Thin wrapper that retries once on 429 / rate-limit errors."""

    def __init__(self, model: str, temperature: float):
        api_key = _get_api_key()
        self._inner = ChatGoogleGenerativeAI(
            model=model, google_api_key=api_key, temperature=temperature,
        )

    def invoke(self, messages):
        try:
            return self._inner.invoke(messages)
        except Exception as e:
            msg = str(e).lower()
            if "429" in msg or "quota" in msg or "rate" in msg:
                # Short backoff then one retry. Free-tier per-minute limits
                # usually reset within a few seconds.
                time.sleep(5)
                return self._inner.invoke(messages)
            raise


def get_llm(temperature: float = 0.2):
    return _RetryingChat(model="gemini-2.5-flash-lite", temperature=temperature)
