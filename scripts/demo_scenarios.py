"""Script chay va ghi lai 4 kich ban demo theo yeu cau Tuan 5 Buoi 5.

1. Tra luat
2. Tinh tro cap
3. Agent tu hoi lai khi thieu thong tin (ask_user)
4. Ra soat hop dong co loi
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage  # noqa: E402
from langgraph.types import Command  # noqa: E402

from src.agent.graph import build_graph  # noqa: E402
from src.agent.nodes import message_text  # noqa: E402
from src.tools.contract_rules import review_contract_file  # noqa: E402

CONTRACTS_DIR = ROOT / "data" / "eval" / "contracts"


def demo_scenario_1_tra_luat(app) -> None:
    print("=" * 70)
    print("KỊCH BẢN 1: TRA CỨU LUẬT LAO ĐỘNG")
    print("=" * 70)
    question = "Thời gian thử việc tối đa đối với người lao động có trình độ chuyên môn kỹ thuật trung cấp là bao nhiêu ngày?"
    print(f"Câu hỏi: {question}\n")

    config = {"configurable": {"thread_id": "demo_scenario_1"}}
    state = {
        "messages": [HumanMessage(question)],
        "evidence": {},
        "tool_calls_count": 0,
        "verify_rounds": 0,
    }
    result = app.invoke(state, config)
    answer = message_text(result["messages"][-1])
    print(f"Agent trả lời:\n{answer}\n")
    print("Các điều luật đã trích:")
    for k, v in result.get("evidence", {}).items():
        if not k.startswith("can_cu:"):
            print(f" - [{k}]: {v[:100]}...")
    print()


def demo_scenario_2_tinh_tro_cap(app) -> None:
    print("=" * 70)
    print("KỊCH BẢN 2: TÍNH TOÁN TRỢ CẤP THÔI VIỆC")
    print("=" * 70)
    question = (
        "Tôi làm việc từ 01/01/2015 đến 31/12/2021 thì nghỉ việc đúng luật. "
        "Mức lương bình quân 6 tháng liền kề là 10.000.000 đồng/tháng. "
        "Thời gian tôi tham gia bảo hiểm thất nghiệp là từ 01/01/2017 đến hết 31/12/2021. "
        "Tính trợ cấp thôi việc công ty phải chi trả cho tôi."
    )
    print(f"Câu hỏi: {question}\n")

    config = {"configurable": {"thread_id": "demo_scenario_2"}}
    state = {
        "messages": [HumanMessage(question)],
        "evidence": {},
        "tool_calls_count": 0,
        "verify_rounds": 0,
    }
    result = app.invoke(state, config)
    answer = message_text(result["messages"][-1])
    print(f"Agent trả lời:\n{answer}\n")


def demo_scenario_3_agent_tu_hoi_lai(app) -> None:
    print("=" * 70)
    print("KỊCH BẢN 3: AGENT TỰ HỎI LẠI KHI THIẾU THÔNG TIN (ask_user)")
    print("=" * 70)
    question = "Tôi muốn nhờ tính tiền trợ cấp thôi việc, lương tôi 12 triệu một tháng."
    print(f"Người dùng gửi lần 1: {question}\n")

    config = {"configurable": {"thread_id": "demo_scenario_3"}}
    state = {
        "messages": [HumanMessage(question)],
        "evidence": {},
        "tool_calls_count": 0,
        "verify_rounds": 0,
    }
    result = app.invoke(state, config)

    if result.get("__interrupt__"):
        interrupted_val = result["__interrupt__"][0].value
        print(f"🤖 Agent ngắt và hỏi lại: {interrupted_val['question']}\n")

        user_reply = (
            "Tôi vào làm việc từ ngày 01/01/2016 và nghỉ việc vào ngày 31/12/2022. "
            "Trong suốt thời gian đó, tôi đóng BHTN từ 01/01/2018 đến 31/12/2022."
        )
        print(f"Người dùng trả lời bổ sung: {user_reply}\n")
        resumed_result = app.invoke(Command(resume=user_reply), config)
        answer = message_text(resumed_result["messages"][-1])
        print(f"Agent trả lời hoàn chỉnh:\n{answer}\n")
    else:
        print("Agent trả lời trực tiếp:", message_text(result["messages"][-1]))


def demo_scenario_4_ra_soat_hop_dong() -> None:
    print("=" * 70)
    print("KỊCH BẢN 4: RÀ SOÁT HỢP ĐỒNG LAO ĐỘNG CÓ LỖI")
    print("=" * 70)
    sample_path = CONTRACTS_DIR / "contract_09_nhieu_loi_1.docx"
    print(f"Tải lên file: {sample_path.name}\n")

    info, warnings = review_contract_file(sample_path)
    print(f"Thông tin trích xuất: {json.dumps(info.model_dump(), ensure_ascii=False, indent=2)}\n")
    print(f"Phát hiện {len(warnings)} cảnh báo vi phạm:")
    for w in warnings:
        print(f" - [⚠️ {w['quy_tac']}]: {w['canh_bao']}")
        print(f"   Căn cứ: [{w['can_cu']}]")
        print(f"   Trích dẫn: {w['trich_dan'][:120]}...\n")


def main() -> None:
    app = build_graph()
    demo_scenario_1_tra_luat(app)
    demo_scenario_2_tinh_tro_cap(app)
    demo_scenario_3_agent_tu_hoi_lai(app)
    demo_scenario_4_ra_soat_hop_dong()
    print("=" * 70)
    print("HOÀN TẤT CẢ 4 KỊCH BẢN DEMO!")
    print("=" * 70)


if __name__ == "__main__":
    main()
