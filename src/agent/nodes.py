"""Cac node cua LangGraph (xem PLAN.md Tuan 3 Buoi 3-4)."""

import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode

from src.agent.prompts import (
    AGENT_SYSTEM_PROMPT,
    CONTRACT_NO_TEXT_MESSAGE,
    OUT_OF_SCOPE_MESSAGE,
    ROUTER_PROMPT,
    VERIFY_FEEDBACK_TEMPLATE,
)
from src.agent.state import AgentState, RouteDecision
from src.agent.tools import ALL_TOOLS
from src.llm import build_llm_chain, message_text, structured_output_transform
from src.tools.contract_rules import check_contract, extract_contract_info

MIN_CONTRACT_TEXT_LEN = 200  # duoi muc nay coi nhu nguoi dung chua dan noi dung hop dong that

MAX_TOOL_CALLS = 6
MAX_VERIFY_ROUNDS = 2

_tool_node = ToolNode(ALL_TOOLS)
_DIEU_RE = re.compile(r"Điều\s+(\d+)", re.IGNORECASE)
_CLAUSE_SPLIT_RE = re.compile(r"[\n.;\[\]]")
_COMPOUND_CONNECTOR_RE = re.compile(
    r"^(?:\s|,|và|hoặc|khoản\s+\d+|điểm\s+[a-zđ])*$", re.IGNORECASE
)
_CHUNK_ID_DIEU_RE = re.compile(r"_D(\d+)_K")
_CHUNK_ID_DOC_DIEU_RE = re.compile(r"^(.+?)_D(\d+)_K")
_DOC_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("BLLD2019", re.compile(r"Bộ\s+luật\s+Lao\s+động|BLLĐ|45/2019", re.IGNORECASE)),
    ("ND145_2020", re.compile(r"Nghị\s+định\s*145|NĐ\s*145|145/2020", re.IGNORECASE)),
    ("ND293_2025", re.compile(r"Nghị\s+định\s*293|NĐ\s*293|293/2025", re.IGNORECASE)),
]


def router(state: AgentState) -> dict:
    llm = build_llm_chain(structured_output_transform(RouteDecision))
    decision = llm.invoke([SystemMessage(ROUTER_PROMPT), *state["messages"]])
    return {"route": decision.route}


def agent_loop(state: AgentState) -> dict:
    llm = build_llm_chain(lambda m: m.bind_tools(ALL_TOOLS))
    messages = [SystemMessage(AGENT_SYSTEM_PROMPT), *state["messages"]]
    response = llm.invoke(messages)
    return {"messages": [response]}


def tools_node(state: AgentState) -> dict:
    """Goi cong cu, dong thoi cong don tool_calls_count va evidence."""
    result = _tool_node.invoke(state)
    evidence = dict(state.get("evidence", {}))
    for msg in result.get("messages", []):
        if not isinstance(msg, ToolMessage) or msg.artifact is None:
            continue
        artifact = msg.artifact
        if isinstance(artifact, list):  # ket qua tu legal_lookup: list[chunk]
            for chunk in artifact:
                evidence[chunk["id"]] = chunk["noi_dung"]
        elif isinstance(artifact, dict) and "can_cu" in artifact:  # ket qua calculator
            for citation in artifact["can_cu"]:
                evidence[f"can_cu:{citation}"] = citation
    return {
        "messages": result.get("messages", []),
        "evidence": evidence,
        "tool_calls_count": state.get("tool_calls_count", 0) + 1,
    }


def should_call_tools(state: AgentState) -> str:
    last = state["messages"][-1]
    has_tool_calls = isinstance(last, AIMessage) and bool(last.tool_calls)
    if has_tool_calls and state.get("tool_calls_count", 0) < MAX_TOOL_CALLS:
        return "tools"
    return "verify_citation"


def _detect_doc_code(text: str) -> str | None:
    """Nhan dien ma van ban chuan hoa tu chuoi trich dan."""
    for doc_code, pattern in _DOC_PATTERNS:
        if pattern.search(text):
            return doc_code
    return None


def _allowed_dieu_numbers(evidence: dict[str, str]) -> set[int]:
    """Chi tin cac Dieu THUC SU duoc tra ve (parse tu key), khong quet noi
    dung chunk -- vi mot chunk co the nhac ("dan chieu") den Dieu khac ma
    KHONG dong nghia Dieu do da duoc tra dung."""
    allowed: set[int] = set()
    for key in evidence:
        chunk_match = _CHUNK_ID_DIEU_RE.search(key)
        if chunk_match:
            allowed.add(int(chunk_match.group(1)))
        elif key.startswith("can_cu:"):
            allowed.update(int(m) for m in _DIEU_RE.findall(key))
    return allowed


def _allowed_doc_dieu_pairs(evidence: dict[str, str]) -> dict[int, set[str]]:
    """Anh xa so_dieu -> tap ma van ban chuan hoa (vd: 'BLLD2019', 'ND145_2020')."""
    pairs: dict[int, set[str]] = {}
    for key in evidence:
        chunk_match = _CHUNK_ID_DOC_DIEU_RE.search(key)
        if chunk_match:
            doc_code = chunk_match.group(1)
            dieu_num = int(chunk_match.group(2))
            pairs.setdefault(dieu_num, set()).add(doc_code)
        elif key.startswith("can_cu:"):
            doc_code = _detect_doc_code(key)
            for m in _DIEU_RE.findall(key):
                dieu_num = int(m)
                docs = pairs.setdefault(dieu_num, set())
                if doc_code is not None:
                    docs.add(doc_code)
    return pairs


def verify_citation(state: AgentState) -> dict:
    last = state["messages"][-1]
    answer = message_text(last).strip()
    rounds = state.get("verify_rounds", 0)

    if not answer:
        rounds += 1
        if rounds >= MAX_VERIFY_ROUNDS:
            return {"verify_rounds": rounds}
        return {
            "verify_rounds": rounds,
            "messages": [SystemMessage("Câu trả lời bị trống. Hãy trả lời lại đầy đủ câu hỏi của người dùng.")],
        }

    evidence = state.get("evidence", {})
    cited = {int(m) for m in _DIEU_RE.findall(answer)}
    allowed = _allowed_dieu_numbers(evidence)
    invalid = cited - allowed

    doc_dieu_pairs = _allowed_doc_dieu_pairs(evidence)
    wrong_doc_notes: list[str] = []
    for match in _DIEU_RE.finditer(answer):
        dieu_num = int(match.group(1))
        if dieu_num in invalid:
            continue
        clause_tail = _CLAUSE_SPLIT_RE.split(answer[match.end() :])[0][:80]
        immediate_tail = _DIEU_RE.split(clause_tail)[0][:40]
        cited_doc = _detect_doc_code(immediate_tail)
        if cited_doc is None and _COMPOUND_CONNECTOR_RE.match(immediate_tail):
            cited_doc = _detect_doc_code(clause_tail)
        allowed_docs = doc_dieu_pairs.get(dieu_num, set())
        if cited_doc is not None and allowed_docs and cited_doc not in allowed_docs:
            invalid.add(dieu_num)
            allowed_str = ", ".join(sorted(allowed_docs))
            wrong_doc_notes.append(
                f"Điều {dieu_num} trong evidence thuộc {allowed_str} (không phải {cited_doc})"
            )

    if not invalid:
        return {}

    rounds += 1
    if rounds >= MAX_VERIFY_ROUNDS:
        return {"verify_rounds": rounds}

    dieu_str = ", ".join(f"Điều {n}" for n in sorted(invalid))
    feedback = VERIFY_FEEDBACK_TEMPLATE.format(dieu_khong_hop_le=dieu_str)
    if wrong_doc_notes:
        feedback += " Lưu ý sai văn bản: " + "; ".join(wrong_doc_notes) + "."
    return {
        "verify_rounds": rounds,
        "messages": [SystemMessage(feedback)],
    }


def should_retry_verify(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, SystemMessage) and state.get("verify_rounds", 0) < MAX_VERIFY_ROUNDS:
        return "agent_loop"
    return "end"


def _format_contract_warnings(warnings: list[dict]) -> str:
    if not warnings:
        body = "Không phát hiện vi phạm nào theo các quy tắc đã kiểm tra."
    else:
        lines = [f"Phát hiện {len(warnings)} cảnh báo:"]
        lines += [f"- {w['canh_bao']} (căn cứ: [{w['can_cu']}])" for w in warnings]
        body = "\n".join(lines)
    return f"{body}\n\nNội dung chỉ mang tính tham khảo, không thay thế tư vấn pháp lý."


def contract_review(state: AgentState) -> dict:
    text = "\n".join(
        message_text(m) for m in state["messages"] if isinstance(m, HumanMessage)
    ).strip()
    if len(text) < MIN_CONTRACT_TEXT_LEN:
        return {"messages": [AIMessage(content=CONTRACT_NO_TEXT_MESSAGE)]}
    info = extract_contract_info(text)
    warnings = check_contract(info)
    return {"messages": [AIMessage(content=_format_contract_warnings(warnings))]}


def out_of_scope(_state: AgentState) -> dict:
    return {"messages": [AIMessage(content=OUT_OF_SCOPE_MESSAGE)]}
