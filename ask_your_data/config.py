"""
Configuration and LLM factory for Ask Your Data.
Supports OpenAI and Anthropic via environment variables. Never hardcodes keys.
"""

import os
from pathlib import Path
from typing import Optional, Any
from dotenv import load_dotenv

# Load .env file from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Settings
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").strip().lower()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o").strip()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_MODEL_NAME = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-5-sonnet-20241022").strip()

SANDBOX_TIMEOUT_SECONDS = int(os.getenv("SANDBOX_TIMEOUT_SECONDS", "5"))

DEFAULT_DATA_PATH = ROOT_DIR / "data" / "master_clean.csv"
DATA_PATH = Path(os.getenv("DATA_PATH", str(DEFAULT_DATA_PATH)))

FASTAPI_HOST = os.getenv("FASTAPI_HOST", "127.0.0.1")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))

SYSTEM_PROMPT = (
    "You are a data analyst assistant for a car dealership. "
    "You answer questions using only the provided dataset via your tools. "
    "Always inspect the schema before writing code. "
    "Never invent numbers; if the data cannot answer a question, say so and explain what is missing. "
    "Prefer simple, verifiable aggregations. "
    "After computing results, explain them for a non-technical sales manager and end with one concrete recommendation. "
    "If the question is ambiguous, state your assumption explicitly."
)


def get_llm(provider: Optional[str] = None) -> Any:
    """
    Factory function returning a LangChain BaseChatModel.
    Provider can be explicitly passed or resolved from LLM_PROVIDER env var.
    If no valid API key is found, returns a MockAnalyticsLLM for offline/demo verification.
    """
    chosen_provider = (provider or LLM_PROVIDER).strip().lower()

    if chosen_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if api_key and not api_key.startswith("your_"):
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=OPENAI_MODEL_NAME,
                    temperature=0.0,
                    api_key=api_key,
                )
            except Exception as e:
                print(f"[Warning] Failed to initialize ChatOpenAI: {e}")
        else:
            print("[Info] No active OPENAI_API_KEY configured. Falling back to MockAnalyticsLLM.")

    elif chosen_provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if api_key and not api_key.startswith("your_"):
            try:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model=ANTHROPIC_MODEL_NAME,
                    temperature=0.0,
                    api_key=api_key,
                )
            except Exception as e:
                print(f"[Warning] Failed to initialize ChatAnthropic: {e}")
        else:
            print("[Info] No active ANTHROPIC_API_KEY configured. Falling back to MockAnalyticsLLM.")

    elif chosen_provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if api_key and not api_key.startswith("your_"):
            try:
                from langchain_groq import ChatGroq
                groq_model = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile").strip()
                return ChatGroq(
                    model_name=groq_model,
                    temperature=0.0,
                    groq_api_key=api_key,
                )
            except Exception as e:
                print(f"[Warning] Failed to initialize ChatGroq: {e}")
        else:
            print("[Info] No active GROQ_API_KEY configured. Falling back to MockAnalyticsLLM.")

    # Fallback mock LLM for offline testing and demo verification
    from ask_your_data.mock_llm import MockAnalyticsLLM
    return MockAnalyticsLLM()
