"""Test cac node cua LangGraph khong can LLM/Qdrant that (mock cac ham goi ra ngoai)."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

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


def test_verify_citation_hop_le_dung_dieu_va_van_ban():
    state = {
        "messages": [
            AIMessage(
                content=(
                    "Thời gian thử việc tối đa là 60 ngày đối với công việc cần trình độ "
                    "cao đẳng trở lên [Điều 25, Bộ luật Lao động 2019]."
                )
            )
        ],
        "evidence": {
            "BLLD2019_D25_K0": "Thời gian thử việc...",
            "can_cu:Điều 46 Bộ luật Lao động 2019": "Điều 46 Bộ luật Lao động 2019",
        },
        "verify_rounds": 0,
    }

    result = nodes.verify_citation(state)

    assert result == {}
    pairs = nodes._allowed_doc_dieu_pairs(state["evidence"])
    assert pairs[25] == {"BLLD2019"}
    assert pairs[46] == {"BLLD2019"}


def test_verify_citation_chan_dieu_khong_co_trong_evidence():
    state = {
        "messages": [
            AIMessage(content="Theo [Điều 99, Bộ luật Lao động 2019], người lao động được nghỉ hưởng nguyên lương.")
        ],
        "evidence": {"BLLD2019_D25_K0": "Thời gian thử việc..."},
        "verify_rounds": 0,
    }

    result = nodes.verify_citation(state)

    assert result["verify_rounds"] == 1
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], SystemMessage)
    assert "Điều 99" in result["messages"][0].content


def test_verify_citation_chan_dung_so_dieu_nhung_sai_van_ban():
    state = {
        "messages": [
            AIMessage(
                content="Người sử dụng lao động phải lập sổ quản lý lao động theo [Điều 8, Bộ luật Lao động 2019]."
            )
        ],
        "evidence": {"ND145_2020_D8_K0": "Điều 8 Nghị định 145/2020/NĐ-CP..."},
        "verify_rounds": 0,
    }

    result = nodes.verify_citation(state)

    assert result["verify_rounds"] == 1
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], SystemMessage)
    assert "Điều 8" in result["messages"][0].content


def test_verify_citation_cau_tra_loi_rong_yeu_cau_tra_loi_lai():
    state = {
        "messages": [AIMessage(content="   ")],
        "evidence": {"BLLD2019_D25_K0": "Thời gian thử việc..."},
        "verify_rounds": 0,
    }

    result = nodes.verify_citation(state)

    assert result["verify_rounds"] == 1
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], SystemMessage)
    assert "trống" in result["messages"][0].content


def test_verify_citation_dat_max_verify_rounds_dung_khong_tra_system_message():
    state = {
        "messages": [AIMessage(content="Theo [Điều 99, Bộ luật Lao động 2019]...")],
        "evidence": {"BLLD2019_D25_K0": "Thời gian thử việc..."},
        "verify_rounds": nodes.MAX_VERIFY_ROUNDS - 1,
    }

    result = nodes.verify_citation(state)

    assert result == {"verify_rounds": nodes.MAX_VERIFY_ROUNDS}
    assert "messages" not in result


def test_verify_citation_bat_loi_gop_nhieu_dieu_khac_van_ban():
    # Dieu 46 thuoc BLLD2019 nhung Dieu 8 thuoc ND145_2020 -> viet gop "Điều 8 và Điều 46 Bộ luật Lao động 2019"
    # hoac "Điều 46 và Điều 8 Bộ luật Lao động 2019" phai bat duoc Dieu 8 sai van ban!
    for text in [
        "Theo Điều 8 và Điều 46 Bộ luật Lao động 2019, người lao động được nhận trợ cấp.",
        "Theo Điều 46 và Điều 8 Bộ luật Lao động 2019, người lao động được nhận trợ cấp.",
        "Theo [điều 8, bộ luật lao động 2019], người lao động được nhận trợ cấp.",
    ]:
        state = {
            "messages": [AIMessage(content=text)],
            "evidence": {
                "BLLD2019_D46_K0": "Điều 46 Bộ luật Lao động 2019...",
                "ND145_2020_D8_K0": "Điều 8 Nghị định 145/2020/NĐ-CP...",
            },
            "verify_rounds": 0,
        }
        result = nodes.verify_citation(state)
        assert result["verify_rounds"] == 1
        assert "Điều 8" in result["messages"][0].content
        assert "ND145_2020" in result["messages"][0].content

