"""Khoi tao LLM (Gemini chinh, Groq du phong), cache va fallback khi loi.

Theo PLAN.md muc 3: temperature=0, luon bat cache, retry khi gap loi 429
va chuyen sang Groq khi Gemini loi lien tuc.
"""

from pathlib import Path

from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from src.config import settings

CACHE_PATH = Path(__file__).resolve().parents[1] / ".langchain_cache.db"
set_llm_cache(SQLiteCache(database_path=str(CACHE_PATH)))


def get_primary_llm() -> BaseChatModel:
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0,
    )


def get_fallback_llm() -> BaseChatModel:
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0,
    )


def invoke_with_fallback(prompt: str, max_retries: int = 2) -> BaseMessage:
    """Goi Gemini truoc; neu loi (vd 429) thi thu lai roi chuyen sang Groq."""
    primary = get_primary_llm()
    last_err: Exception | None = None
    for _ in range(max_retries):
        try:
            return primary.invoke(prompt)
        except Exception as e:  # noqa: BLE001 -- can bat moi loi de fallback sang Groq
            last_err = e
    try:
        return get_fallback_llm().invoke(prompt)
    except Exception as e:
        raise RuntimeError(
            f"Ca Gemini va Groq deu loi. Gemini: {last_err}. Groq: {e}"
        ) from e
