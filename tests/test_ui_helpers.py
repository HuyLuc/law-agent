"""Unit test cho cac ham dinh dang giao dien trong src/ui/app.py."""

from src.ui.app import (
    _extract_api_error,
    _iter_sse,
    format_chunk_label,
    format_extracted_contract_summary,
    format_step_log,
)


def test_format_chunk_label_standard_docs():
    assert format_chunk_label("BLLD2019_D25_K0") == "📖 BLLĐ 2019 — Điều 25"
    assert format_chunk_label("BLLD2019_D41_K2") == "📖 BLLĐ 2019 — Điều 41 Khoản 2"
    assert format_chunk_label("ND145_2020_D8_K3") == "📖 NĐ 145/2020 — Điều 8 Khoản 3"
    assert format_chunk_label("ND293_2025_D3_K0") == "📖 NĐ 293/2025 — Điều 3"
    assert format_chunk_label("custom_id") == "📖 custom_id"


def test_format_step_log_tool_calls_and_text():
    step_tc = {
        "node": "agent_loop",
        "tool_calls": [{"name": "get_article_tool", "args": {"van_ban": "Bộ luật Lao động 2019", "dieu": 25}}],
    }
    lines_tc = format_step_log(step_tc)
    assert len(lines_tc) == 1
    assert "get_article_tool" in lines_tc[0]

    step_txt = {"node": "verify", "text": "Câu trả lời hợp lệ"}
    lines_txt = format_step_log(step_txt)
    assert len(lines_txt) == 1
    assert "verify" in lines_txt[0]

    assert format_step_log({"node": "router"}) == []


def test_format_extracted_contract_summary():
    sample_info = {
        "loai_hop_dong": "xac_dinh_thoi_han",
        "thoi_han_hop_dong_thang": 12,
        "vi_tri_cong_viec": "Kỹ sư phần mềm",
        "trinh_do_yeu_cau": "cao_dang_tro_len",
        "so_ngay_thu_viec": 60,
        "luong_thu_viec": 17_000_000,
        "luong_chinh": 20_000_000,
        "vung_luong_toi_thieu": "I",
        "gio_lam_ngay": 8.0,
        "gio_lam_tuan": 40.0,
        "co_bhxh": False,
        "co_dao_tao": False,
    }
    general_rows, checklist = format_extracted_contract_summary(sample_info)
    rows_dict = dict(general_rows)
    assert rows_dict["Loại hợp đồng"] == "Xác định thời hạn"
    assert rows_dict["Thời hạn hợp đồng"] == "12 tháng"
    assert rows_dict["Mức lương chính thức"] == "20.000.000 đ/tháng"
    assert rows_dict["Giờ làm việc / ngày"] == "8 giờ/ngày"
    assert rows_dict["Giờ làm việc / tuần"] == "40 giờ/tuần"
    assert len(checklist) == 9
    failed_items = [label for label, ok in checklist if not ok]
    assert len(failed_items) == 2


def test_format_extracted_contract_summary_empty_fields():
    general_rows, checklist = format_extracted_contract_summary({})
    rows_dict = dict(general_rows)
    assert rows_dict["Loại hợp đồng"] == "Chưa xác định"
    assert rows_dict["Thời hạn hợp đồng"] == "Không áp dụng / Chưa rõ"
    assert rows_dict["Mức lương chính thức"] == "Chưa xác định"
    assert all(ok for _, ok in checklist)


def test_iter_sse_va_extract_api_error():
    class _FakeStreamResp:
        def iter_lines(self, decode_unicode=True):
            assert decode_unicode is True
            return iter(
                [
                    None,
                    "event: meta",
                    'data: {"thread_id": "t-123"}',
                    "",
                    "event: done",
                    "data: {}",
                    "",
                ]
            )

    events = list(_iter_sse(_FakeStreamResp()))
    assert events == [("meta", {"thread_id": "t-123"}), ("done", {})]

    class _FakeJsonErrResp:
        status_code = 400
        text = '{"detail": "Chỉ hỗ trợ file .pdf hoặc .docx"}'

        def json(self):
            return {"detail": "Chỉ hỗ trợ file .pdf hoặc .docx"}

    class _FakeTextErrResp:
        status_code = 502
        text = "Bad Gateway"

        def json(self):
            raise ValueError("Not JSON")

    assert _extract_api_error(_FakeJsonErrResp()) == "Chỉ hỗ trợ file .pdf hoặc .docx"
    assert _extract_api_error(_FakeTextErrResp()) == "Bad Gateway"
