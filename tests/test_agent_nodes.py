"""Test cac node cua LangGraph khong can LLM/Qdrant that (mock cac ham goi ra ngoai)."""

from langchain_core.messages import HumanMessage

from src.agent import nodes
from src.tools.contract_rules import ContractInfo


def test_contract_review_thieu_noi_dung_hoi_lai(monkeypatch):
    called = False

    def _fake_extract(_text):
        nonlocal called
        called = True
        return ContractInfo()

    monkeypatch.setattr(nodes, "extract_contract_info", _fake_extract)
    state = {"messages": [HumanMessage("rà soát hợp đồng giúp tôi")]}

    result = nodes.contract_review(state)

    assert not called
    assert "dán" in result["messages"][0].content


def test_contract_review_co_vi_pham_liet_ke_canh_bao(monkeypatch):
    long_text = "Hợp đồng lao động " + "nội dung chi tiết " * 20

    monkeypatch.setattr(nodes, "extract_contract_info", lambda _text: ContractInfo(gio_lam_ngay=10))
    monkeypatch.setattr(
        nodes,
        "check_contract",
        lambda _info: [
            {"quy_tac": "gio_lam_ngay", "canh_bao": "Giờ làm việc vượt quá 8 giờ/ngày.", "can_cu": "Điều 105"}
        ],
    )
    state = {"messages": [HumanMessage(long_text)]}

    result = nodes.contract_review(state)
    content = result["messages"][0].content

    assert "Giờ làm việc vượt quá" in content
    assert "Điều 105" in content


def test_contract_review_khong_vi_pham(monkeypatch):
    long_text = "Hợp đồng lao động " + "nội dung chi tiết " * 20

    monkeypatch.setattr(nodes, "extract_contract_info", lambda _text: ContractInfo())
    monkeypatch.setattr(nodes, "check_contract", lambda _info: [])
    state = {"messages": [HumanMessage(long_text)]}

    result = nodes.contract_review(state)

    assert "Không phát hiện vi phạm" in result["messages"][0].content
