"""Test cac quy tac kiem tra hop dong (khong can Qdrant/LLM that -- mock
get_article de test nhanh, xac dinh)."""

import io

import pytest
from docx import Document

from src.tools import contract_rules as cr
from src.tools.contract_rules import ContractInfo, check_contract, export_contract_review_docx


@pytest.fixture(autouse=True)
def _mock_get_article(monkeypatch):
    monkeypatch.setattr(
        cr, "get_article", lambda _van_ban, dieu, _khoan=None: [{"noi_dung": f"[noi dung Dieu {dieu}]"}]
    )


def _hop_le(**overrides) -> ContractInfo:
    base = {
        "loai_hop_dong": "khong_xac_dinh_thoi_han",
        "vi_tri_cong_viec": "Nhân viên văn phòng",
        "trinh_do_yeu_cau": "trung_cap",
        "so_ngay_thu_viec": 25,
        "luong_thu_viec": 8_500_000,
        "luong_chinh": 10_000_000,
        "vung_luong_toi_thieu": "I",
        "gio_lam_ngay": 8,
        "gio_lam_tuan": 44,
    }
    base.update(overrides)
    return ContractInfo(**base)


def test_hop_dong_hop_le_khong_co_canh_bao():
    assert check_contract(_hop_le()) == []


def test_thu_viec_qua_han_bi_canh_bao():
    info = _hop_le(trinh_do_yeu_cau="trung_cap", so_ngay_thu_viec=45)
    warnings = check_contract(info)
    assert any(w["quy_tac"] == "thoi_gian_thu_viec" for w in warnings)


def test_thu_viec_dung_han_khong_bi_canh_bao():
    info = _hop_le(trinh_do_yeu_cau="quan_ly", so_ngay_thu_viec=150)
    warnings = check_contract(info)
    assert not any(w["quy_tac"] == "thoi_gian_thu_viec" for w in warnings)


def test_luong_thu_viec_duoi_85_phan_tram_bi_canh_bao():
    info = _hop_le(luong_chinh=10_000_000, luong_thu_viec=7_000_000)
    warnings = check_contract(info)
    assert any(w["quy_tac"] == "luong_thu_viec" for w in warnings)


def test_luong_thu_viec_dung_85_phan_tram_khong_bi_canh_bao():
    info = _hop_le(luong_chinh=10_000_000, luong_thu_viec=8_500_000)
    warnings = check_contract(info)
    assert not any(w["quy_tac"] == "luong_thu_viec" for w in warnings)


def test_luong_duoi_toi_thieu_vung_bi_canh_bao():
    info = _hop_le(vung_luong_toi_thieu="I", luong_chinh=4_000_000)
    warnings = check_contract(info)
    assert any(w["quy_tac"] == "luong_toi_thieu_vung" for w in warnings)


def test_gio_lam_ngay_vuot_qua_bi_canh_bao():
    info = _hop_le(gio_lam_ngay=10)
    warnings = check_contract(info)
    assert any(w["quy_tac"] == "gio_lam_ngay" for w in warnings)


def test_gio_lam_tuan_vuot_qua_bi_canh_bao():
    info = _hop_le(gio_lam_tuan=50)
    warnings = check_contract(info)
    assert any(w["quy_tac"] == "gio_lam_tuan" for w in warnings)


def test_thieu_noi_dung_bat_buoc_bi_canh_bao():
    info = _hop_le(co_bhxh=False, co_dao_tao=False)
    warnings = check_contract(info)
    match = [w for w in warnings if w["quy_tac"] == "noi_dung_bat_buoc"]
    assert len(match) == 1
    assert "bảo hiểm" in match[0]["canh_bao"]
    assert "đào tạo" in match[0]["canh_bao"]


def test_thieu_thong_tin_khong_bao_gio_bao_canh_bao_gia() -> None:
    """Neu thieu du lieu (None) thi khong the ket luan vi pham -- khong duoc
    canh bao khong co can cu."""
    info = ContractInfo()
    assert check_contract(info) == []


def test_export_contract_review_docx_co_canh_bao() -> None:
    info = _hop_le(trinh_do_yeu_cau="trung_cap", so_ngay_thu_viec=45, gio_lam_ngay=10)
    warnings = check_contract(info)
    docx_bytes = export_contract_review_docx(info, warnings, source_filename="hd_vi_pham.docx")
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 0

    doc = Document(io.BytesIO(docx_bytes))
    full_text = "\n".join(p.text for p in doc.paragraphs)
    assert "BÁO CÁO RÀ SOÁT HỢP ĐỒNG LAO ĐỘNG" in full_text
    assert "hd_vi_pham.docx" in full_text
    assert "Phát hiện 2 cảnh báo vi phạm:" in full_text
    assert "Điều 25 Bộ luật Lao động 2019" in full_text
    assert "Điều 105 Bộ luật Lao động 2019" in full_text
    assert "Lưu ý: Báo cáo này được tạo tự động bởi AI Agent" in full_text


def test_export_contract_review_docx_hop_le_khong_canh_bao() -> None:
    info = _hop_le()
    warnings = check_contract(info)
    assert warnings == []

    docx_bytes = export_contract_review_docx(info, warnings, source_filename="hd_hop_le.pdf")
    doc = Document(io.BytesIO(docx_bytes))
    full_text = "\n".join(p.text for p in doc.paragraphs)
    assert "BÁO CÁO RÀ SOÁT HỢP ĐỒNG LAO ĐỘNG" in full_text
    assert "hd_hop_le.pdf" in full_text
    assert "Không phát hiện điều khoản vi phạm theo các quy tắc kiểm tra hiện hành" in full_text
    assert "Nhân viên văn phòng" in full_text


def test_export_contract_review_docx_all_none_va_thieu_trich_dan() -> None:
    info = ContractInfo()
    warnings = [
        {
            "quy_tac": "gio_lam_ngay",
            "canh_bao": "Giờ làm việc vượt quá 8 giờ/ngày.",
            "can_cu": "Điều 105 Bộ luật Lao động 2019",
        }
    ]
    docx_bytes = export_contract_review_docx(info, warnings)
    doc = Document(io.BytesIO(docx_bytes))
    full_text = "\n".join(p.text for p in doc.paragraphs)

    assert "None" not in full_text
    assert "Chưa xác định" in full_text
    assert "Giờ làm việc vượt quá 8 giờ/ngày." in full_text
    assert "Điều 105 Bộ luật Lao động 2019" in full_text
    assert "Trích dẫn điều luật:" not in full_text


def test_api_export_contract_docx_endpoint() -> None:
    from fastapi import HTTPException

    from src.api.main import ContractReportRequest, export_contract_docx

    info = _hop_le()
    req = ContractReportRequest(
        extracted_info=info.model_dump(),
        warnings=[],
        filename="hợp_đồng_lao_động.docx",
    )
    resp = export_contract_docx(req)
    assert resp.status_code == 200
    assert resp.media_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    doc = Document(io.BytesIO(resp.body))
    full_text = "\n".join(p.text for p in doc.paragraphs)
    assert "hợp_đồng_lao_động.docx" in full_text

    bad_req = ContractReportRequest(
        extracted_info={"loai_hop_dong": "loai_khong_ton_tai"},
        warnings=[],
    )
    with pytest.raises(HTTPException) as exc_info:
        export_contract_docx(bad_req)
    assert exc_info.value.status_code == 422
