"""Cac node cua LangGraph (xem PLAN.md Tuan 3 Buoi 3-4)."""

import re

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode

from src.agent.prompts import (
    AGENT_SYSTEM_PROMPT,
    CONTRACT_STUB_MESSAGE,
    OUT_OF_SCOPE_MESSAGE,
    ROUTER_PROMPT,
    VERIFY_FEEDBACK_TEMPLATE,
)
from src.agent.state import AgentState, RouteDecision
from src.agent.tools import ALL_TOOLS
from src.llm import get_primary_llm

MAX_TOOL_CALLS = 6
MAX_VERIFY_ROUNDS = 2

_tool_node = ToolNode(ALL_TOOLS)
_DIEU_RE = re.compile(r"Điều\s+(\d+)")


def message_text(message) -> str:
    """Lay phan text thuan tuy tu AIMessage.content (co the la str hoac list block)."""
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


def router(state: AgentState) -> dict:
    llm = get_primary_llm().with_structured_output(RouteDecision)
    decision = llm.invoke([SystemMessage(ROUTER_PROMPT), *state["messages"]])
    return {"route": decision.route}


def agent_loop(state: AgentState) -> dict:
    llm = get_primary_llm().bind_tools(ALL_TOOLS)
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


def verify_citation(state: AgentState) -> dict:
    last = state["messages"][-1]
    answer = message_text(last)
    cited = {int(m) for m in _DIEU_RE.findall(answer)}

    allowed: set[int] = set()
    for content in state.get("evidence", {}).values():
        allowed.update(int(m) for m in _DIEU_RE.findall(content))

    invalid = cited - allowed
    if not invalid:
        return {}

    rounds = state.get("verify_rounds", 0) + 1
    if rounds >= MAX_VERIFY_ROUNDS:
        return {"verify_rounds": rounds}

    dieu_str = ", ".join(f"Điều {n}" for n in sorted(invalid))
    feedback = VERIFY_FEEDBACK_TEMPLATE.format(dieu_khong_hop_le=dieu_str)
    return {
        "verify_rounds": rounds,
        "messages": [SystemMessage(feedback)],
    }


def should_retry_verify(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, SystemMessage) and state.get("verify_rounds", 0) < MAX_VERIFY_ROUNDS:
        return "agent_loop"
    return "end"


def contract_review(_state: AgentState) -> dict:
    return {"messages": [AIMessage(content=CONTRACT_STUB_MESSAGE)]}


def out_of_scope(_state: AgentState) -> dict:
    return {"messages": [AIMessage(content=OUT_OF_SCOPE_MESSAGE)]}
