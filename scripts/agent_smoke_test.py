"""Chay agent tren N cau dev.jsonl, luu lai toan bo vet (trace) de doc lai
tung buoc (PLAN.md Tuan 3 Buoi 5). Bo qua cau can ask_user vi khong the
tra loi tu dong trong script nay.

Chay: python scripts/agent_smoke_test.py
"""

import json
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.agent.graph import build_graph
from src.agent.nodes import message_text

ROOT = Path(__file__).resolve().parents[1]
DEV_PATH = ROOT / "data" / "eval" / "dev.jsonl"
OUT_PATH = ROOT / "scripts" / "agent_smoke_test_output.txt"

QUESTION_IDS = [
    "d001", "d016", "d017", "d021", "d024",
    "d028", "d030", "d034", "d036", "d039",
]


def run_one(question: str, thread_id: str) -> dict:
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
        return {"interrupted": True, "question_payload": result["__interrupt__"][0].value}

    trace = []
    for msg in result["messages"]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            trace.append({"tool_calls": [(tc["name"], tc["args"]) for tc in msg.tool_calls]})
        elif isinstance(msg, ToolMessage):
            trace.append({"tool_result_preview": str(msg.content)[:200]})

    return {
        "route": result.get("route"),
        "trace": trace,
        "final_answer": message_text(result["messages"][-1]),
        "verify_rounds": result.get("verify_rounds", 0),
    }


def main() -> None:
    dev = {json.loads(line)["id"]: json.loads(line) for line in DEV_PATH.open(encoding="utf-8")}

    with OUT_PATH.open("w", encoding="utf-8") as f:
        for qid in QUESTION_IDS:
            item = dev[qid]
            f.write(f"{'=' * 80}\n{qid} [{item['loai']}] {item['question']}\n")
            f.write(f"--- ground_truth: {item['ground_truth']}\n")
            f.write(f"--- dieu_can_trich: {item['dieu_can_trich']}\n\n")
            try:
                result = run_one(item["question"], thread_id=qid)
            except Exception as e:  # noqa: BLE001
                f.write(f"LOI: {e}\n\n")
                print(qid, "LOI:", e)
                continue
            f.write(json.dumps(result, ensure_ascii=False, indent=2))
            f.write("\n\n")
            f.flush()
            print(qid, "xong")

    print(f"Da ghi ket qua vao {OUT_PATH}")


if __name__ == "__main__":
    main()
