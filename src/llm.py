"""Khoi tao LLM (Gemini chinh, Groq du phong), cache va fallback khi loi.

Theo PLAN.md muc 3: temperature=0, luon bat cache, retry khi gap loi 429
va chuyen sang Groq khi Gemini loi lien tuc.
"""

from collections.abc import Callable
from pathlib import Path

from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from src.config import settings

CACHE_PATH = Path(__file__).resolve().parents[1] / ".langchain_cache.db"
set_llm_cache(SQLiteCache(database_path=str(CACHE_PATH)))


def get_gemini_llms() -> list[BaseChatModel]:
    """Mot ChatGoogleGenerativeAI cho MOI key trong settings.gemini_api_keys,
    de xoay vong khi 1 key het quota (free tier chi ~20 request/ngay)."""
    return [
        ChatGoogleGenerativeAI(model=settings.LLM_MODEL, google_api_key=key, temperature=0)
        for key in settings.gemini_api_keys
    ]


def get_primary_llm() -> BaseChatModel:
    """Tra ve Gemini dau tien (dung khi khong can xoay vong nhieu key)."""
    return get_gemini_llms()[0]


def get_fallback_llm() -> BaseChatModel:
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0,
    )


def build_llm_chain(transform: Callable[[BaseChatModel], Runnable] = lambda m: m) -> Runnable:
    """Ap dung `transform` (vd .bind_tools(...), .with_structured_output(...))
    cho tung Gemini key roi Groq, sau do noi lai bang with_fallbacks: thu key 1,
    het quota/loi thi tu dong sang key 2, ..., cuoi cung moi roi xuong Groq."""
    models = [transform(m) for m in get_gemini_llms()] + [transform(get_fallback_llm())]
    primary, *rest = models
    return primary.with_fallbacks(rest)


def invoke_with_fallback(prompt: str) -> BaseMessage:
    """Goi lan luot tung Gemini key, het quota/loi thi chuyen sang Groq."""
    return build_llm_chain().invoke(prompt)
