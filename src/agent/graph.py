"""Dung graph agent va CLI don gian de thu nhanh.

Chay: python -m src.agent.graph "câu hỏi"
"""

import sys

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from src.agent.nodes import (
    agent_loop,
    contract_review,
    message_text,
    out_of_scope,
    router,
    should_call_tools,
    should_retry_verify,
    tools_node,
    verify_citation,
)
from src.agent.state import AgentState


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("router", router)
    graph.add_node("agent_loop", agent_loop)
    graph.add_node("tools", tools_node)
    graph.add_node("verify_citation", verify_citation)
    graph.add_node("contract_review", contract_review)
    graph.add_node("out_of_scope", out_of_scope)

    graph.add_edge(START, "router")
    graph.add_conditional_edges(
        "router",
        lambda s: s["route"],
        {"legal_qa": "agent_loop", "contract": "contract_review", "out_of_scope": "out_of_scope"},
    )
    graph.add_conditional_edges(
        "agent_loop", should_call_tools, {"tools": "tools", "verify_citation": "verify_citation"}
    )
    graph.add_edge("tools", "agent_loop")
    graph.add_conditional_edges(
        "verify_citation", should_retry_verify, {"agent_loop": "agent_loop", "end": END}
    )
    graph.add_edge("contract_review", END)
    graph.add_edge("out_of_scope", END)

    return graph.compile(checkpointer=MemorySaver())


def run_cli(question: str) -> str:
    app = build_graph()
    config = {"configurable": {"thread_id": "cli"}}
    state = {
        "messages": [HumanMessage(question)],
        "evidence": {},
        "tool_calls_count": 0,
        "verify_rounds": 0,
    }
    result = app.invoke(state, config)

    while result.get("__interrupt__"):
        question_payload = result["__interrupt__"][0].value
        answer = input(f"[Agent hỏi] {question_payload['question']}\n> ")
        result = app.invoke(Command(resume=answer), config)

    return message_text(result["messages"][-1])


def main() -> None:
    question = " ".join(sys.argv[1:]) or input("Câu hỏi: ")
    print(run_cli(question))


if __name__ == "__main__":
    main()
