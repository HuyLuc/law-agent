"""Khoi tao LLM (Gemini chinh, Groq du phong), cache va fallback khi loi.

Theo PLAN.md muc 3: temperature=0, luon bat cache, retry khi gap loi 429
va chuyen sang Groq khi Gemini loi lien tuc.
"""

import json
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from src.config import settings

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = ROOT / ".langchain_cache.db"
set_llm_cache(SQLiteCache(database_path=str(CACHE_PATH)))

DEAD_KEYS_PATH = ROOT / ".gemini_dead_keys.json"

# Quota free-tier tinh RIENG cho tung model (khong chi rieng tung key), nen
# khi het quota model chinh (settings.LLM_MODEL) o TAT CA key, van con co the
# goi duoc cac model flash khac cung key do. Danh sach nay la cac ban flash
# on dinh (khong phai "-preview"/"-lite"/"-image"/"-tts") con ton tai tai
# thoi diem lam du an (kiem tra qua genai Client.models.list()).
GEMINI_MODEL_FALLBACKS = ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash"]


def get_gemini_llms() -> list[BaseChatModel]:
    """Mot ChatGoogleGenerativeAI cho MOI to hop (model, key): thu het cac
    key voi model chinh (settings.LLM_MODEL) truoc -- giu nguyen hanh vi cu
    khi quota con -- roi moi sang cac model du phong o GEMINI_MODEL_FALLBACKS
    khi ca 5 key deu da het quota voi model chinh."""
    models = [settings.LLM_MODEL, *[m for m in GEMINI_MODEL_FALLBACKS if m != settings.LLM_MODEL]]
    return [
        ChatGoogleGenerativeAI(model=model_name, google_api_key=key, temperature=0)
        for model_name in models
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


# Index (trong danh sach tra ve boi get_gemini_llms(), tuc tung to hop
# key x model) da biet het quota HOM NAY. Dung .with_fallbacks() cua
# LangChain se thu lai het moi to hop moi lan goi du da biet chet (lang phi
# ~30-50s/lan khi quota het het ca ngay) -- nho lai o day
# (ca trong bo nho va ghi ra file) de bo qua thang tu process khac trong
# cung ngay, chi con Groq la fallback thuc su huu ich luc do. Tu dong reset
# khi sang ngay moi (quota Gemini free tier tinh theo ngay).


def _load_dead_keys() -> set[int]:
    if not DEAD_KEYS_PATH.exists():
        return set()
    try:
        data = json.loads(DEAD_KEYS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    if data.get("date") != datetime.now().astimezone().date().isoformat():
        return set()
    return set(data.get("dead_indices", []))


def _save_dead_keys(dead_indices: set[int]) -> None:
    DEAD_KEYS_PATH.write_text(
        json.dumps({"date": datetime.now().astimezone().date().isoformat(), "dead_indices": sorted(dead_indices)}),
        encoding="utf-8",
    )


_dead_gemini_keys: set[int] = _load_dead_keys()


def _is_key_unusable_error(exc: Exception) -> bool:
    """Loi ma retry lai cung key nay se khong bao gio thanh cong: het quota
    (429), model khong kha dung cho key nay (404), hoac tai khoan bi tu
    choi quyen (403). Danh dau key chet ngay, khong lang phi thoi gian thu
    lai."""
    msg = str(exc)
    return any(code in msg for code in ["RESOURCE_EXHAUSTED", "429", "NOT_FOUND", "404", "PERMISSION_DENIED", "403"])


GROQ_RETRY_ATTEMPTS = 3  # Groq la tuyen cuoi khi Gemini het sach quota: mot lan JSON
# sinh sai dinh dang (glitch thoang qua cua model, khong phai loi logic) khong nen
# lam sap ca batch eval nhieu gio chay -- thu lai vai lan truoc khi bo cuoc.


def _invoke_groq_with_retry(groq_model: Runnable, *args, **kwargs):
    last_err: Exception | None = None
    for attempt in range(GROQ_RETRY_ATTEMPTS):
        try:
            return groq_model.invoke(*args, **kwargs)
        except Exception as e:  # noqa: BLE001 -- can bat moi loi de thu lai
            last_err = e
            if attempt < GROQ_RETRY_ATTEMPTS - 1:
                time.sleep(3)
    raise last_err


class _ChainWithKeyMemory:
    def __init__(self, gemini_models: list[Runnable], groq_model: Runnable) -> None:
        self._gemini_models = gemini_models
        self._groq_model = groq_model

    def invoke(self, *args, **kwargs):
        last_err: Exception | None = None
        for i, model in enumerate(self._gemini_models):
            if i in _dead_gemini_keys:
                continue
            try:
                return model.invoke(*args, **kwargs)
            except Exception as e:  # noqa: BLE001 -- can bat moi loi de thu key/Groq tiep theo
                last_err = e
                if _is_key_unusable_error(e) and i not in _dead_gemini_keys:
                    _dead_gemini_keys.add(i)
                    _save_dead_keys(_dead_gemini_keys)
        try:
            return _invoke_groq_with_retry(self._groq_model, *args, **kwargs)
        except Exception as e:
            con_lai = len(self._gemini_models) - len(_dead_gemini_keys)
            raise RuntimeError(
                f"Tat ca to hop Gemini (key x model) con hoat dong ({con_lai}) va Groq deu loi. "
                f"Loi Gemini gan nhat: {last_err}. Loi Groq: {e}"
            ) from e


def build_llm_chain(transform: Callable[[BaseChatModel], Runnable] = lambda m: m) -> _ChainWithKeyMemory:
    """Ap dung `transform` (vd .bind_tools(...), .with_structured_output(...))
    cho tung Gemini key roi Groq. Thu lan luot cac key CHUA biet het quota,
    het quota/loi thi tu dong sang key tiep theo, cuoi cung moi roi xuong Groq."""
    gemini_models = [transform(m) for m in get_gemini_llms()]
    groq_model = transform(get_fallback_llm())
    return _ChainWithKeyMemory(gemini_models, groq_model)


def structured_output_transform(schema: type) -> Callable[[BaseChatModel], Runnable]:
    """Transform dung cho build_llm_chain khi can output co cau truc (Pydantic
    schema). Groq (model openai/gpt-oss-20b) hay loi "Tool choice is required,
    but model did not call a tool" voi method mac dinh (function_calling) --
    dung json_schema cho rieng Groq de tranh loi nay; Gemini van dung mac dinh
    (da kiem chung hoat dong tot qua nhieu lan goi that)."""

    def _transform(model: BaseChatModel) -> Runnable:
        if isinstance(model, ChatGroq):
            return model.with_structured_output(schema, method="json_schema")
        return model.with_structured_output(schema)

    return _transform


def invoke_with_fallback(prompt: str) -> BaseMessage:
    """Goi lan luot tung Gemini key, het quota/loi thi chuyen sang Groq."""
    return build_llm_chain().invoke(prompt)


def message_text(message: BaseMessage) -> str:
    """Lay phan text thuan tuy tu AIMessage.content (co the la str hoac list
    block -- Gemini 3.x tra ve list block thuong xuyen hon 2.x)."""
    content = message.content
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block["text"])
        elif isinstance(block, str):
            parts.append(block)
    return "\n".join(parts)
