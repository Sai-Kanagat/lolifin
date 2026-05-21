"""
LLM client config. Uses Gemini 2.0 Flash (free tier).

Why Gemini Flash:
- 100% free at https://aistudio.google.com/app/apikey
- 15 requests/min, 1M tokens/day on the free tier (plenty for this project)
- Native structured-output (JSON mode) and tool calling
- Fast (sub-second) which matters when 5 agents run sequentially

If quota is ever hit during a demo, swap to Groq (also free) — change one import.
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def get_llm(temperature: float = 0.2) -> ChatGoogleGenerativeAI:
    """
    Returns a configured Gemini chat model.

    temperature=0.2 keeps outputs deterministic enough for finance work
    while still allowing the editor agent to write fluent prose.
    """
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
            "(or to Streamlit secrets when deploying)."
        )

    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=temperature,
    )
