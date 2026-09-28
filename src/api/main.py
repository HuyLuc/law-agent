"""FastAPI cho agent tu van Luat Lao dong (PLAN.md Tuan 5 Buoi 1).

Chay: uvicorn src.api.main:app --reload
"""

import json
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from pydantic import BaseModel

from src.agent.graph import build_graph
from src.config import settings
from src.llm import message_text
from src.retrieval.hybrid import get_client
from src.tools.contract_rules import review_contract_file

app = FastAPI(title="VN Labor Law Agent API")
_graph = build_graph()


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ResumeRequest(BaseModel):
    answer: str
    thread_id: str


def _new_state(message: str) -> dict:
    return {
        "messages": [HumanMessage(message)],
        "evidence": {},
        "tool_calls_count": 0,
        "verify_rounds": 0,
    }


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _stream_graph_events(graph_input, config: dict, thread_id: str):
    yield _sse("meta", {"thread_id": thread_id})
    for event in _graph.stream(graph_input, config, stream_mode="updates"):
        for node_name, node_output in event.items():
            if node_name == "__interrupt__":
                payload = node_output[0].value
                yield _sse("interrupt", payload)
                return
            step: dict = {"node": node_name}
            if "evidence" in node_output:
                step["evidence"] = node_output["evidence"]
            for msg in node_output.get("messages", []):
                if getattr(msg, "tool_calls", None):
                    step.setdefault("tool_calls", []).extend(
                        {"name": tc["name"], "args": tc["args"]} for tc in msg.tool_calls
                    )
                else:
                    text = message_text(msg)
                    if text:
                        step["text"] = text
            yield _sse("step", step)
    yield _sse("done", {})


@app.post("/chat")
def chat(req: ChatRequest):
    thread_id = req.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    return StreamingResponse(
        _stream_graph_events(_new_state(req.message), config, thread_id),
        media_type="text/event-stream",
    )


@app.post("/chat/resume")
def chat_resume(req: ResumeRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    return StreamingResponse(
        _stream_graph_events(Command(resume=req.answer), config, req.thread_id),
        media_type="text/event-stream",
    )


@app.post("/review-contract")
async def review_contract(file: UploadFile = File(...)):  # noqa: B008 -- pattern chuan cua FastAPI
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in (".pdf", ".docx"):
        raise HTTPException(400, "Chỉ hỗ trợ file .pdf hoặc .docx")

    content = await file.read()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    try:
        info, warnings = review_contract_file(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    return {"extracted_info": info.model_dump(), "warnings": warnings}


@app.get("/health")
def health():
    status: dict = {"api": "ok"}
    try:
        get_client().get_collections()
        status["qdrant"] = "ok"
    except Exception as e:  # noqa: BLE001 -- health check can bat moi loi de bao cao
        status["qdrant"] = f"error: {e}"
    status["llm_configured"] = bool(settings.gemini_api_keys or settings.GROQ_API_KEY)
    return status
