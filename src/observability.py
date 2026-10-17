"""Observability va tracing cho agent (PLAN.md Tuan 6 muc 4).

Ho tro Langfuse Cloud de theo doi tung lan chay agent, latency, token va doan hoi thoai.
Neu chua cai langfuse hoac chua cau hinh key trong .env thi tu dong bo qua,
khong lam anh huong den runtime.
"""

import logging
from typing import Any

from src.config import settings

logger = logging.getLogger(__name__)


def get_callbacks(session_id: str | None = None) -> list[Any]:
    """Tra ve danh sach callbacks cho LangChain / LangGraph invocation.

    Neu co LANGFUSE_PUBLIC_KEY va LANGFUSE_SECRET_KEY, khoi tao CallbackHandler.
    """
    if not (settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY):
        return []

    try:
        from langfuse.callback import CallbackHandler

        handler = CallbackHandler(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
            session_id=session_id,
        )
        return [handler]
    except ImportError:
        logger.warning(
            "Langfuse key da duoc cau hinh nhung package 'langfuse' chua duoc cai dat. "
            "Chay `pip install langfuse` de bat tracing len Langfuse Cloud."
        )
        return []
    except Exception as e:  # noqa: BLE001 -- an toàn cho optional observability
        logger.warning(f"Khong the khoi tao Langfuse CallbackHandler: {e}")
        return []
