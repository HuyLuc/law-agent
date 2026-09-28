"""Cac phien ban tra loi cau hoi (V0-V4), dung de danh gia trong Tuan 4.

Moi ham answer_vN(question) -> (answer_text, retrieved_chunks). retrieved_chunks
rong doi voi V0 (khong tra cuu).
"""

from langchain_core.messages import HumanMessage

from src.agent.graph import build_graph
from src.agent.nodes import message_text
from src.llm import invoke_with_fallback
from src.retrieval.hybrid import search_dense, search_hybrid
from src.retrieval.reranker import search_reranked

V0_SYSTEM_PROMPT = (
    "Ban la tro ly tra loi cau hoi ve Luat Lao dong Viet Nam. Tra loi ngan gon, "
    "chinh xac nhat co the. Cuoi cau tra loi ghi ro: 'Noi dung chi mang tinh tham "
    "khao, khong thay the tu van phap ly.'"
)

RAG_SYSTEM_PROMPT = """Ban la tro ly tu van Luat Lao dong Viet Nam.

QUY TAC BAT BUOC:
1. Chi tra loi dua tren thong tin trong phan "Ngu canh" duoi day. Neu ngu canh
   khong du de tra loi, noi ro "khong tim thay can cu" thay vi doan.
2. Moi nhan dinh phap ly phai kem trich dan dang [Dieu X, <ten van ban>].
3. Ket thuc bang: "Noi dung chi mang tinh tham khao, khong thay the tu van phap ly."
"""


def _format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "(khong co ngu canh)"
    return "\n\n".join(
        f"[{c['id']}] Điều {c['dieu']}"
        + (f" Khoản {c['khoan']}" if c.get("khoan") else "")
        + f" - {c['van_ban']}\n{c['noi_dung']}"
        for c in chunks
    )


def _answer_with_context(question: str, chunks: list[dict]) -> tuple[str, list[dict]]:
    context = _format_context(chunks)
    prompt = f"{RAG_SYSTEM_PROMPT}\n\nNgữ cảnh:\n{context}\n\nCâu hỏi: {question}"
    answer = invoke_with_fallback(prompt).content
    return answer, chunks


def answer_v0(question: str) -> tuple[str, list[dict]]:
    prompt = f"{V0_SYSTEM_PROMPT}\n\nCau hoi: {question}"
    return invoke_with_fallback(prompt).content, []


def answer_v1(question: str) -> tuple[str, list[dict]]:
    return _answer_with_context(question, search_dense(question, top_k=5))


def answer_v2(question: str) -> tuple[str, list[dict]]:
    return _answer_with_context(question, search_hybrid(question, top_k=5))


def answer_v3(question: str) -> tuple[str, list[dict]]:
    return _answer_with_context(question, search_reranked(question, top_k=5))


def answer_v4(question: str, thread_id: str) -> tuple[str, list[dict]]:
    """V4 = agent day du. Neu agent goi ask_user (interrupt) thi coi nhu chua
    tra loi duoc (danh gia tu dong khong the doi thoai nhieu vong)."""
    app = build_graph()
    config = {"configurable": {"thread_id": thread_id}}
    state = {
        "messages": [HumanMessage(question)],
        "evidence": {},
        "tool_calls_count": 0,
        "verify_rounds": 0,
    }
    result = app.invoke(state, config)
    if result.get("__interrupt__"):
        return "[AGENT_INTERRUPTED]", []
    evidence = result.get("evidence", {})
    chunks = [{"id": k, "noi_dung": v} for k, v in evidence.items() if not k.startswith("can_cu:")]
    return message_text(result["messages"][-1]), chunks
