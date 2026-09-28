"""Streamlit UI cho agent tu van Luat Lao dong (PLAN.md Tuan 5 Buoi 2).

Chay: streamlit run src/ui/app.py
(Yeu cau FastAPI dang chay: uvicorn src.api.main:app)
"""

import json
import os
import uuid

import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Tư vấn Luật Lao động Việt Nam", page_icon="⚖️", layout="wide")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user"|"assistant", "content": str}]
if "evidence" not in st.session_state:
    st.session_state.evidence = {}  # chunk_id -> noi_dung
if "pending_interrupt" not in st.session_state:
    st.session_state.pending_interrupt = None  # cau hoi cua ask_user, cho nguoi dung tra loi


def _iter_sse(response):
    event, data_lines = None, []
    for raw_line in response.iter_lines(decode_unicode=True):
        if raw_line is None:
            continue
        line = raw_line.strip("\n")
        if line.startswith("event:"):
            event = line.removeprefix("event:").strip()
        elif line.startswith("data:"):
            data_lines.append(line.removeprefix("data:").strip())
        elif line == "" and event is not None:
            data = json.loads("\n".join(data_lines)) if data_lines else {}
            yield event, data
            event, data_lines = None, []


def _render_step(step: dict, steps_box) -> str | None:
    """Ve 1 buoc agent da lam, cap nhat evidence. Tra ve text cau tra loi cuoi (neu co)."""
    if "evidence" in step:
        st.session_state.evidence.update(step["evidence"])
    node = step.get("node", "?")
    with steps_box:
        if step.get("tool_calls"):
            for tc in step["tool_calls"]:
                st.caption(f"🔧 `{node}` gọi công cụ **{tc['name']}**({tc['args']})")
        elif step.get("text"):
            st.caption(f"📝 `{node}`: {step['text'][:200]}")
    if node == "agent_loop" and step.get("text") and not step.get("tool_calls"):
        return step["text"]
    return None


def _consume_stream(response, steps_box) -> str:
    final_answer = ""
    for event, data in _iter_sse(response):
        if event == "meta":
            st.session_state.thread_id = data["thread_id"]
        elif event == "interrupt":
            st.session_state.pending_interrupt = data["question"]
        elif event == "step":
            text = _render_step(data, steps_box)
            if text:
                final_answer = text
        elif event == "done":
            break
    return final_answer


# ---------------------------------------------------------------------------
# Sidebar: cac dieu luat da trich

with st.sidebar:
    st.header("📚 Điều luật đã tra")
    if not st.session_state.evidence:
        st.caption("Chưa có điều luật nào được tra cứu.")
    for chunk_id, noi_dung in st.session_state.evidence.items():
        if chunk_id.startswith("can_cu:"):
            continue
        with st.expander(chunk_id):
            st.text(noi_dung)

# ---------------------------------------------------------------------------
# Tabs: chat + ra soat hop dong

tab_chat, tab_contract = st.tabs(["💬 Hỏi đáp", "📄 Rà soát hợp đồng"])

with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if st.session_state.pending_interrupt:
        st.info(f"🤖 Agent hỏi: {st.session_state.pending_interrupt}")
        answer = st.chat_input("Trả lời câu hỏi của agent...")
        if answer:
            st.session_state.messages.append({"role": "user", "content": answer})
            with st.chat_message("user"):
                st.write(answer)
            st.session_state.pending_interrupt = None
            with st.chat_message("assistant"):
                steps_box = st.container()
                resp = requests.post(
                    f"{API_URL}/chat/resume",
                    json={"answer": answer, "thread_id": st.session_state.thread_id},
                    stream=True,
                    timeout=120,
                )
                final_answer = _consume_stream(resp, steps_box)
                if final_answer:
                    st.write(final_answer)
                    st.session_state.messages.append({"role": "assistant", "content": final_answer})
            st.rerun()
    else:
        question = st.chat_input("Hỏi về Luật Lao động Việt Nam...")
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.write(question)
            with st.chat_message("assistant"):
                steps_box = st.container()
                resp = requests.post(
                    f"{API_URL}/chat",
                    json={"message": question, "thread_id": st.session_state.thread_id},
                    stream=True,
                    timeout=120,
                )
                final_answer = _consume_stream(resp, steps_box)
                if final_answer:
                    st.write(final_answer)
                    st.session_state.messages.append({"role": "assistant", "content": final_answer})
            st.rerun()

with tab_contract:
    st.write("Tải lên hợp đồng lao động (.pdf hoặc .docx) để kiểm tra các điều khoản.")
    uploaded = st.file_uploader("Chọn file hợp đồng", type=["pdf", "docx"])
    if uploaded and st.button("Rà soát hợp đồng"):
        with st.spinner("Đang đọc và kiểm tra hợp đồng..."):
            resp = requests.post(
                f"{API_URL}/review-contract",
                files={"file": (uploaded.name, uploaded.getvalue())},
                timeout=180,
            )
        if resp.status_code != 200:
            st.error(resp.json().get("detail", "Có lỗi xảy ra."))
        else:
            result = resp.json()
            warnings = result["warnings"]
            if not warnings:
                st.success("Không phát hiện vi phạm nào theo các quy tắc đã kiểm tra.")
            else:
                st.warning(f"Phát hiện {len(warnings)} cảnh báo:")
                for w in warnings:
                    with st.expander(f"⚠️ {w['canh_bao']}"):
                        st.write(f"**Căn cứ:** {w['can_cu']}")
                        st.text(w["trich_dan"])
            with st.expander("Thông tin đã trích xuất từ hợp đồng"):
                st.json(result["extracted_info"])
