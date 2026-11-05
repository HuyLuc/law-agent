"""Streamlit UI cho agent tu van Luat Lao dong (PLAN.md Tuan 5 Buoi 2).

Chay: streamlit run src/ui/app.py
(Yeu cau FastAPI dang chay: uvicorn src.api.main:app)
"""

import json
import os
import re
import uuid
from pathlib import Path

import requests
import streamlit as st

from src.tools.contract_rules import ContractInfo, export_contract_review_docx

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
ROOT_DIR = Path(__file__).resolve().parents[2]
SAMPLE_CONTRACTS_DIR = ROOT_DIR / "data" / "eval" / "contracts"
CACHED_CONTRACT_EVAL_PATH = ROOT_DIR / "eval" / "results" / "contract_review.json"
CHUNKS_PATH = ROOT_DIR / "data" / "processed" / "chunks.jsonl"

QUICK_PROMPTS = [
    (
        "📜 Thời gian thử việc tối đa",
        "Thời gian thử việc tối đa đối với vị trí yêu cầu trình độ trung cấp là bao nhiêu ngày?",
    ),
    (
        "💰 Tính trợ cấp thôi việc",
        "Làm việc 24 tháng, đóng BHTN 12 tháng, lương bình quân 12 triệu thì trợ cấp thôi việc tính thế nào?",
    ),
    (
        "⚖️ Bồi thường sa thải trái luật",
        "Công ty đơn phương chấm dứt HĐLĐ trái luật, lương 15 triệu/tháng, nghỉ chờ 2 tháng, "
        "đã làm 36 tháng (BHTN 24 tháng) và vi phạm báo trước 15 ngày thì bồi thường bao nhiêu?",
    ),
    (
        "🤔 Câu hỏi thiếu dữ kiện (Demo hỏi lại)",
        "Tính giúp tôi tiền trợ cấp thôi việc khi nghỉ việc.",
    ),
]

SAMPLE_CONTRACT_DESCRIPTIONS = {
    "contract_01_dung.docx": "Hợp đồng chuẩn #1 (Đầy đủ, hợp lệ)",
    "contract_02_dung.docx": "Hợp đồng chuẩn #2 (Đầy đủ, hợp lệ)",
    "contract_03_loi_thu_viec.docx": "Vi phạm thời gian thử việc (Điều 25)",
    "contract_04_loi_luong_thu_viec.docx": "Vi phạm lương thử việc < 85% (Điều 26)",
    "contract_05_loi_luong_toi_thieu.docx": "Vi phạm lương tối thiểu vùng (NĐ 293/2025)",
    "contract_06_loi_gio_ngay.docx": "Vi phạm giờ làm việc/ngày > 8h (Điều 105)",
    "contract_07_loi_gio_tuan.docx": "Vi phạm giờ làm việc/tuần > 48h (Điều 105)",
    "contract_08_loi_thieu_noi_dung.docx": "Thiếu nội dung bắt buộc (Điều 21)",
    "contract_09_nhieu_loi_1.docx": "Hợp đồng tổng hợp nhiều lỗi vi phạm #1",
    "contract_10_nhieu_loi_2.docx": "Hợp đồng tổng hợp nhiều lỗi vi phạm #2",
}

_LOAI_HD_UI = {
    "khong_xac_dinh_thoi_han": "Không xác định thời hạn",
    "xac_dinh_thoi_han": "Xác định thời hạn",
}

_TRINH_DO_UI = {
    "quan_ly": "Người quản lý doanh nghiệp",
    "cao_dang_tro_len": "Từ cao đẳng trở lên",
    "trung_cap": "Trung cấp / CNKT / Nghiệp vụ",
    "khac": "Lao động phổ thông (khác)",
}

_DIEU_21_CHECKLIST = [
    ("co_thong_tin_cac_ben", "Tên, địa chỉ người sử dụng lao động và người lao động"),
    ("co_cong_viec_dia_diem", "Công việc và địa điểm làm việc"),
    ("co_thoi_han", "Thời hạn của hợp đồng lao động"),
    ("co_muc_luong", "Mức lương theo công việc/chức danh, hình thức và kỳ hạn trả lương"),
    ("co_che_do_nang_luong", "Chế độ nâng bậc, nâng lương"),
    ("co_thoi_gio_lam_viec_nghi_ngoi", "Thời giờ làm việc, thời giờ nghỉ ngơi"),
    ("co_trang_bi_bao_ho", "Trang bị bảo hộ lao động cho người lao động"),
    ("co_bhxh", "Bảo hiểm xã hội, bảo hiểm y tế và bảo hiểm thất nghiệp"),
    ("co_dao_tao", "Đào tạo, bồi dưỡng, nâng cao trình độ, kỹ năng nghề"),
]


def format_chunk_label(chunk_id: str) -> str:
    """Chuyen ma chunk_id (VD: BLLD2019_D25_K0) thanh nhan hien thi de doc."""
    m = re.match(r"^([A-Za-z0-9_]+)_D(\d+)_K(\d+)$", chunk_id.strip())
    if not m:
        return f"📖 {chunk_id}"
    doc_code, dieu, khoan = m.group(1), int(m.group(2)), int(m.group(3))
    doc_map = {
        "BLLD2019": "BLLĐ 2019",
        "ND145_2020": "NĐ 145/2020",
        "ND293_2025": "NĐ 293/2025",
    }
    doc_label = doc_map.get(doc_code, doc_code)
    khoan_str = f" Khoản {khoan}" if khoan > 0 else ""
    return f"📖 {doc_label} — Điều {dieu}{khoan_str}"


def format_step_log(step: dict) -> list[str]:
    """Trich xuat danh sach dong mo ta buoc suy luan/goi cong cu cua agent."""
    node = step.get("node", "?")
    lines: list[str] = []
    if step.get("tool_calls"):
        for tc in step["tool_calls"]:
            lines.append(f"🔧 `{node}` gọi công cụ **{tc['name']}**({tc['args']})")
    elif step.get("text"):
        lines.append(f"📝 `{node}`: {step['text'][:200]}")
    return lines


def format_extracted_contract_summary(
    info_dict: dict,
) -> tuple[list[tuple[str, str]], list[tuple[str, bool]]]:
    """Chuyen dict ContractInfo thanh bang thong tin chung va checklist Dieu 21."""
    loai_hd = _LOAI_HD_UI.get(info_dict.get("loai_hop_dong") or "", "Chưa xác định")
    thoi_han = (
        f"{info_dict['thoi_han_hop_dong_thang']} tháng"
        if info_dict.get("thoi_han_hop_dong_thang") is not None
        else "Không áp dụng / Chưa rõ"
    )
    vi_tri = info_dict.get("vi_tri_cong_viec") or "Chưa xác định"
    trinh_do = _TRINH_DO_UI.get(info_dict.get("trinh_do_yeu_cau") or "", "Chưa xác định")
    thu_viec = (
        f"{info_dict['so_ngay_thu_viec']} ngày"
        if info_dict.get("so_ngay_thu_viec") is not None
        else "Chưa xác định"
    )
    luong_tv = (
        f"{info_dict['luong_thu_viec']:,.0f} đ/tháng".replace(",", ".")
        if info_dict.get("luong_thu_viec") is not None
        else "Chưa xác định"
    )
    luong_chinh = (
        f"{info_dict['luong_chinh']:,.0f} đ/tháng".replace(",", ".")
        if info_dict.get("luong_chinh") is not None
        else "Chưa xác định"
    )
    vung = (
        f"Vùng {info_dict['vung_luong_toi_thieu']}"
        if info_dict.get("vung_luong_toi_thieu")
        else "Chưa xác định"
    )
    gio_ngay = (
        f"{info_dict['gio_lam_ngay']:g} giờ/ngày"
        if info_dict.get("gio_lam_ngay") is not None
        else "Chưa xác định"
    )
    gio_tuan = (
        f"{info_dict['gio_lam_tuan']:g} giờ/tuần"
        if info_dict.get("gio_lam_tuan") is not None
        else "Chưa xác định"
    )

    general_rows = [
        ("Loại hợp đồng", loai_hd),
        ("Thời hạn hợp đồng", thoi_han),
        ("Vị trí công việc", vi_tri),
        ("Trình độ chuyên môn", trinh_do),
        ("Thời gian thử việc", thu_viec),
        ("Mức lương thử việc", luong_tv),
        ("Mức lương chính thức", luong_chinh),
        ("Vùng lương tối thiểu", vung),
        ("Giờ làm việc / ngày", gio_ngay),
        ("Giờ làm việc / tuần", gio_tuan),
    ]
    checklist = [(label, bool(info_dict.get(field, True))) for field, label in _DIEU_21_CHECKLIST]
    return general_rows, checklist


def _extract_api_error(resp: requests.Response) -> str:
    """Trich xuat thong bao loi than thien tu HTTP response khong thanh cong."""
    try:
        detail = resp.json().get("detail")
        if detail:
            return str(detail)
    except ValueError:
        pass
    return resp.text or f"Máy chủ trả về mã lỗi HTTP {resp.status_code}."


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


def _render_step(step: dict, steps_box, steps_log: list[str] | None = None) -> str | None:
    """Ve 1 buoc agent da lam, cap nhat evidence. Tra ve text cau tra loi cuoi (neu co)."""
    if "evidence" in step:
        st.session_state.evidence.update(step["evidence"])
    node = step.get("node", "?")
    log_lines = format_step_log(step)
    if steps_log is not None:
        steps_log.extend(log_lines)
    with steps_box:
        for line in log_lines:
            st.caption(line)
    if node in ("agent_loop", "out_of_scope", "contract_review") and step.get("text") and not step.get("tool_calls"):
        return step["text"]
    return None


def _consume_stream(response, steps_box, steps_log: list[str] | None = None) -> str:
    final_answer = ""
    for event, data in _iter_sse(response):
        if event == "meta":
            st.session_state.thread_id = data["thread_id"]
        elif event == "interrupt":
            st.session_state.pending_interrupt = data["question"]
        elif event == "step":
            text = _render_step(data, steps_box, steps_log)
            if text:
                final_answer = text
        elif event == "done":
            break
    return final_answer


@st.cache_data(ttl=10, show_spinner=False)
def _check_backend_health(api_url: str) -> dict:
    """Kiem tra nhanh /health voi cache 10s de moi thao tac UI phan hoi tuc thi."""
    try:
        resp = requests.get(f"{api_url}/health", timeout=0.4)
        if resp.status_code == 200:
            return {"online": True, "data": resp.json()}
        return {"online": False, "code": resp.status_code}
    except requests.RequestException:
        return {"online": False}


def _is_running_in_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:  # noqa: BLE001
        return False


def _load_local_article_text(so_hieu_or_ten: str, dieu: int) -> str:
    """Doc noi dung Dieu luat tu chunks.jsonl cuc bo (dung khi xem nhanh mau offline)."""
    if not CHUNKS_PATH.exists():
        return ""
    try:
        with CHUNKS_PATH.open(encoding="utf-8") as f:
            for line in f:
                c = json.loads(line)
                if c.get("dieu") == dieu and (
                    c.get("van_ban") == so_hieu_or_ten or c.get("so_hieu") == so_hieu_or_ten
                ):
                    return c.get("noi_dung", "")
    except OSError:
        return ""
    return ""


def _build_offline_sample_review(filename: str) -> dict | None:
    """Tao ket qua ra soat cho hop dong mau tu du lieu da kiem chung."""
    if not CACHED_CONTRACT_EVAL_PATH.exists():
        return None
    try:
        eval_data = json.loads(CACHED_CONTRACT_EVAL_PATH.read_text(encoding="utf-8"))
        file_entry = eval_data.get("per_file", {}).get(filename)
        if not file_entry or "extracted_info" not in file_entry:
            return None
        extracted = file_entry["extracted_info"]
        info = ContractInfo(**extracted)
        from src.tools import contract_rules as cr

        warnings: list[dict] = []
        if info.so_ngay_thu_viec is not None and info.trinh_do_yeu_cau is not None:
            limit = cr.GIOI_HAN_THU_VIEC_NGAY[info.trinh_do_yeu_cau]
            if info.so_ngay_thu_viec > limit:
                warnings.append(
                    {
                        "quy_tac": "thoi_gian_thu_viec",
                        "canh_bao": (
                            f"Thời gian thử việc {info.so_ngay_thu_viec} ngày vượt quá mức tối đa cho phép "
                            f"({limit} ngày) đối với vị trí này."
                        ),
                        "can_cu": "Điều 25 Bộ luật Lao động 2019",
                        "trich_dan": _load_local_article_text("Bộ luật Lao động 2019", 25),
                    }
                )
        if info.luong_thu_viec is not None and info.luong_chinh is not None:
            muc_tt = 0.85 * info.luong_chinh
            if info.luong_thu_viec < muc_tt:
                warnings.append(
                    {
                        "quy_tac": "luong_thu_viec",
                        "canh_bao": (
                            f"Lương thử việc {info.luong_thu_viec:,.0f}đ thấp hơn mức tối thiểu 85% lương chính "
                            f"({muc_tt:,.0f}đ)."
                        ),
                        "can_cu": "Điều 26 Bộ luật Lao động 2019",
                        "trich_dan": _load_local_article_text("Bộ luật Lao động 2019", 26),
                    }
                )
        if info.luong_chinh is not None and info.vung_luong_toi_thieu is not None:
            muc_vung = cr.LUONG_TOI_THIEU_VUNG[info.vung_luong_toi_thieu]
            if info.luong_chinh < muc_vung:
                warnings.append(
                    {
                        "quy_tac": "luong_toi_thieu_vung",
                        "canh_bao": (
                            f"Lương chính {info.luong_chinh:,.0f}đ thấp hơn mức lương tối thiểu Vùng "
                            f"{info.vung_luong_toi_thieu} ({muc_vung:,.0f}đ)."
                        ),
                        "can_cu": "Điều 3 Nghị định 293/2025/NĐ-CP",
                        "trich_dan": _load_local_article_text("293/2025/NĐ-CP", 3),
                    }
                )
        if info.gio_lam_ngay is not None and info.gio_lam_ngay > 8:
            warnings.append(
                {
                    "quy_tac": "gio_lam_ngay",
                    "canh_bao": f"Giờ làm việc {info.gio_lam_ngay:g} giờ/ngày vượt quá 8 giờ/ngày.",
                    "can_cu": "Điều 105 Bộ luật Lao động 2019",
                    "trich_dan": _load_local_article_text("Bộ luật Lao động 2019", 105),
                }
            )
        if info.gio_lam_tuan is not None and info.gio_lam_tuan > 48:
            warnings.append(
                {
                    "quy_tac": "gio_lam_tuan",
                    "canh_bao": f"Giờ làm việc {info.gio_lam_tuan:g} giờ/tuần vượt quá 48 giờ/tuần.",
                    "can_cu": "Điều 105 Bộ luật Lao động 2019",
                    "trich_dan": _load_local_article_text("Bộ luật Lao động 2019", 105),
                }
            )
        missing = [ten for field, ten in cr._NOI_DUNG_BAT_BUOC if not getattr(info, field)]
        if missing:
            warnings.append(
                {
                    "quy_tac": "noi_dung_bat_buoc",
                    "canh_bao": "Hợp đồng thiếu nội dung bắt buộc: " + "; ".join(missing) + ".",
                    "can_cu": "Điều 21 Bộ luật Lao động 2019",
                    "trich_dan": _load_local_article_text("Bộ luật Lao động 2019", 21),
                }
            )
        return {"extracted_info": extracted, "warnings": warnings}
    except Exception:  # noqa: BLE001
        return None


def _load_demo_conversation() -> None:
    """Nap hoi thoai mau sinh dong de nguoi dung xem ngay bo cuc giao dien."""
    d46 = _load_local_article_text("Bộ luật Lao động 2019", 46) or (
        "Điều 46. Trợ cấp thôi việc\n1. Khi hợp đồng lao động chấm dứt theo quy định..."
    )
    d8_nd145 = _load_local_article_text("145/2020/NĐ-CP", 8) or (
        "Điều 8. Trợ cấp thôi việc, trợ cấp mất việc làm\n3. Thời gian làm việc để tính trợ cấp..."
    )
    st.session_state.evidence = {
        "BLLD2019_D46_K0": d46,
        "ND145_2020_D8_K0": d8_nd145,
    }
    st.session_state.messages = [
        {
            "role": "user",
            "content": (
                "Tôi làm việc tại công ty được 30 tháng, đã tham gia bảo hiểm thất nghiệp 18 tháng. "
                "Lương bình quân 6 tháng liền kề trước khi nghỉ việc hợp pháp là 14.000.000 đồng/tháng. "
                "Xin hỏi tôi được nhận trợ cấp thôi việc bao nhiêu tiền?"
            ),
        },
        {
            "role": "assistant",
            "steps": [
                "📝 `router`: Phân loại câu hỏi vào nhánh `legal_qa` (tính toán trợ cấp thôi việc theo luật lao động).",
                "🔧 `agent_loop` gọi công cụ **get_article_tool**({'van_ban': 'Bộ luật Lao động 2019', 'dieu': 46})",
                "🔧 `agent_loop` gọi công cụ **tinh_tro_cap_thoi_viec_tool**"
                "({'thoi_gian_lam_viec_thang': 30, 'thoi_gian_dong_bhtn_thang': 18, 'luong_bq_6_thang': 14000000})",
                "📝 `verify_citation`: Kiểm chứng hợp lệ 100% trích dẫn ([Điều 46, Bộ luật Lao động 2019], "
                "[Điều 8, Nghị định 145/2020/NĐ-CP]).",
            ],
            "content": (
                "Dựa trên thông tin bạn cung cấp, khoản **trợ cấp thôi việc** của bạn được xác định như sau:\n\n"
                "### 1. Kết quả tính toán\n"
                "- **Tổng thời gian làm việc thực tế:** 30 tháng\n"
                "- **Thời gian đã đóng BHTN:** 18 tháng\n"
                "- **Thời gian tính trợ cấp thôi việc:** `30 - 18 = 12 tháng` (**1.0 năm tròn**)\n"
                "- **Mức trợ cấp thôi việc được nhận:** `1.0 năm × 0.5 tháng × 14.000.000đ` = **7.000.000 đồng**\n\n"
                "### 2. Căn cứ pháp lý\n"
                "- Theo **[Điều 46, Bộ luật Lao động 2019]**, người lao động đã làm việc thường xuyên từ đủ 12 tháng "
                "trở lên khi chấm dứt hợp đồng lao động đúng quy định được hưởng trợ cấp thôi việc, mỗi năm làm việc "
                "được trợ cấp một nửa tháng tiền lương.\n"
                "- Theo **[Điều 8, Nghị định 145/2020/NĐ-CP]**, thời gian làm việc để tính trợ cấp thôi việc là tổng "
                "thời gian người lao động đã làm việc thực tế trừ đi thời gian đã tham gia bảo hiểm thất nghiệp.\n\n"
                "*Nội dung chỉ mang tính tham khảo, không thay thế tư vấn pháp lý.*"
            ),
        },
    ]
    st.session_state.pending_interrupt = None


def render_app() -> None:
    st.set_page_config(page_title="Tư vấn Luật Lao động Việt Nam", page_icon="⚖️", layout="wide")

    st.markdown(
        """<style>
        /* Tổng thể khoảng cách trang */
        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1220px;
        }
        /* Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #1d4ed8 100%);
            color: #f8fafc;
            padding: 1.65rem 2rem;
            border-radius: 18px;
            margin-bottom: 1.4rem;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.18);
            border: 1px solid rgba(148, 163, 184, 0.25);
            position: relative;
            overflow: hidden;
        }
        .hero-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            flex-wrap: wrap;
        }
        .hero-kicker {
            display: inline-block;
            background: rgba(251, 191, 36, 0.18);
            color: #fde68a;
            border: 1px solid rgba(251, 191, 36, 0.4);
            font-size: 0.74rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            margin-bottom: 0.55rem;
        }
        .hero-title {
            font-size: 1.75rem;
            font-weight: 800;
            margin: 0 0 0.4rem 0;
            letter-spacing: -0.02em;
            color: #ffffff;
        }
        .hero-subtitle {
            font-size: 0.95rem;
            color: #dbeafe;
            margin: 0;
            line-height: 1.5;
        }
        .hero-stats {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
        }
        .hero-stat-box {
            background: rgba(15, 23, 42, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 12px;
            padding: 0.55rem 0.9rem;
            text-align: center;
            min-width: 98px;
            backdrop-filter: blur(8px);
        }
        .hero-stat-num {
            font-size: 1.15rem;
            font-weight: 800;
            color: #fbbf24;
            line-height: 1.2;
        }
        .hero-stat-label {
            font-size: 0.72rem;
            color: #cbd5e1;
            margin-top: 0.15rem;
        }
        .badge-row {
            margin-top: 1rem;
            padding-top: 0.85rem;
            border-top: 1px solid rgba(255, 255, 255, 0.14);
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .legal-badge {
            background: rgba(255, 255, 255, 0.13);
            color: #f1f5f9;
            padding: 0.26rem 0.75rem;
            border-radius: 999px;
            font-size: 0.79rem;
            font-weight: 500;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        /* Thẻ tính năng & quy tắc */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.85rem;
            margin: 0.6rem 0 1.25rem 0;
        }
        .feature-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #2563eb;
            border-radius: 12px;
            padding: 0.85rem 1rem;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        }
        .feature-card-title {
            font-weight: 700;
            font-size: 0.9rem;
            color: #0f172a;
            margin-bottom: 0.25rem;
        }
        .feature-card-desc {
            font-size: 0.81rem;
            color: #475569;
            margin: 0;
            line-height: 1.45;
        }
        /* Quy tắc hợp đồng */
        .rule-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 0.5rem 0 1.1rem 0;
        }
        .rule-pill {
            background: #eff6ff;
            color: #1e40af;
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            padding: 0.35rem 0.75rem;
            font-size: 0.81rem;
            font-weight: 600;
        }
        /* Nút gợi ý câu hỏi */
        div.stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.15s ease-in-out !important;
        }
        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
        }
        /* Metric cards */
        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-top: 3px solid #2563eb;
            padding: 0.95rem 1.15rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        }
        /* Bảng thông tin hợp đồng */
        .info-panel {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem 1.2rem;
        }
        .status-box {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 0.7rem 0.85rem;
            margin-bottom: 0.75rem;
            font-size: 0.84rem;
            line-height: 1.65;
        }
        </style>
<div class="hero-banner">
<div class="hero-top">
<div>
<span class="hero-kicker">✨ LegalTech AI · LangGraph + Hybrid RAG</span>
<div class="hero-title">⚖️ AI Agent Tư vấn Luật Lao động Việt Nam</div>
<p class="hero-subtitle">
Tra cứu điều luật có kiểm chứng trích dẫn · Tính toán chính xác bằng Python · Rà soát hợp đồng tự động
</p>
</div>
<div class="hero-stats">
<div class="hero-stat-box">
<div class="hero-stat-num">379</div>
<div class="hero-stat-label">Đơn vị Điều/Khoản</div>
</div>
<div class="hero-stat-box">
<div class="hero-stat-num">98.8%</div>
<div class="hero-stat-label">Retrieval Hit@5</div>
</div>
<div class="hero-stat-box">
<div class="hero-stat-num">100%</div>
<div class="hero-stat-label">Chống trích dẫn bịa</div>
</div>
</div>
</div>
<div class="badge-row">
<span class="legal-badge">📕 Bộ luật Lao động 45/2019/QH14 (220 Điều)</span>
<span class="legal-badge">📘 Nghị định 145/2020/NĐ-CP (115 Điều)</span>
<span class="legal-badge">📗 Nghị định 293/2025/NĐ-CP (Lương tối thiểu 2026)</span>
<span class="legal-badge">🧮 6 Công cụ tính toán Python thuần</span>
</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []  # [{"role": "user"|"assistant", "content": str, "steps": list[str]}]
    if "evidence" not in st.session_state:
        st.session_state.evidence = {}  # chunk_id -> noi_dung
    if "pending_interrupt" not in st.session_state:
        st.session_state.pending_interrupt = None  # cau hoi cua ask_user, cho nguoi dung tra loi
    if "last_contract_review" not in st.session_state:
        st.session_state.last_contract_review = None
    if "queued_question" not in st.session_state:
        st.session_state.queued_question = None

    # ---------------------------------------------------------------------------
    # Sidebar: Trang thai he thong + Hoi thoai moi + Cac dieu luat da trich

    with st.sidebar:
        st.subheader("🖥️ Trạng thái hệ thống")
        health_info = _check_backend_health(API_URL)
        if health_info.get("online"):
            h_data = health_info["data"]
            qdrant_ok = h_data.get("qdrant") == "ok"
            llm_ok = bool(h_data.get("llm_configured"))
            st.markdown(
                f"""<div class="status-box">
🟢 <b>FastAPI:</b> Sẵn sàng<br>
{'🟢' if qdrant_ok else '🟡'} <b>Qdrant:</b> {'Đã kết nối' if qdrant_ok else h_data.get('qdrant')}<br>
{'🟢' if llm_ok else '🔴'} <b>LLM:</b> {'Đã cấu hình' if llm_ok else 'Chưa cấu hình API key'}
</div>""",
                unsafe_allow_html=True,
            )
        elif "code" in health_info:
            st.caption(f"🟡 **API:** Phản hồi mã {health_info['code']}")
        else:
            st.markdown(
                f"""<div class="status-box">
🟢 <b>Giao diện UI:</b> Sẵn sàng<br>
🟡 <b>API Backend:</b> Chế độ Demo cục bộ<br>
<span style="color:#64748b;font-size:0.78rem;">Endpoint: {API_URL}</span>
</div>""",
                unsafe_allow_html=True,
            )

        sb_col1, sb_col2 = st.columns(2)
        with sb_col1:
            if st.button("🔄 Làm mới", use_container_width=True, help="Bắt đầu cuộc trò chuyện mới"):
                st.session_state.thread_id = str(uuid.uuid4())
                st.session_state.messages = []
                st.session_state.evidence = {}
                st.session_state.pending_interrupt = None
                st.session_state.queued_question = None
                st.rerun()
        with sb_col2:
            if st.button("🎬 Xem mẫu", use_container_width=True, help="Nạp phiên hội thoại mẫu có trích dẫn"):
                _load_demo_conversation()
                st.rerun()

        st.divider()
        legal_chunks = {
            cid: text
            for cid, text in st.session_state.evidence.items()
            if not cid.startswith("can_cu:")
        }
        st.subheader(f"📚 Điều luật đã tra ({len(legal_chunks)})")
        if not legal_chunks:
            st.caption("Chưa có điều luật nào được tra cứu trong phiên này.")
        for chunk_id, noi_dung in legal_chunks.items():
            with st.expander(format_chunk_label(chunk_id)):
                st.caption(f"Mã trích dẫn: `{chunk_id}`")
                st.text(noi_dung)

    # ---------------------------------------------------------------------------
    # Tabs: chat + ra soat hop dong

    tab_chat, tab_contract = st.tabs(["💬 Hỏi đáp Pháp lý", "📄 Rà soát Hợp đồng"])

    with tab_chat:
        if not st.session_state.messages and not st.session_state.pending_interrupt:
            st.markdown(
                """<div class="feature-grid">
<div class="feature-card">
<div class="feature-card-title">🔍 Hybrid RAG + ONNX Rerank</div>
<p class="feature-card-desc">
Kết hợp tìm kiếm ngữ nghĩa Dense + từ khóa Sparse (BGE-M3) và Reranker đạt Hit@5 98.8%.
</p>
</div>
<div class="feature-card">
<div class="feature-card-title">🧮 6 Công cụ Tính toán Python</div>
<p class="feature-card-desc">
Tính chính xác trợ cấp thôi việc, mất việc, làm thêm giờ, phép năm, báo trước & bồi thường Điều 41.
</p>
</div>
<div class="feature-card">
<div class="feature-card-title">🛡️ Kiểm chứng Trích dẫn Đa văn bản</div>
<p class="feature-card-desc">
Tự động đối chiếu chéo từng cặp (Số Điều, Văn bản) với nguồn đã tra và tự hỏi lại khi thiếu dữ kiện.
</p>
</div>
</div>""",
                unsafe_allow_html=True,
            )
            st.markdown("##### 💡 Gợi ý câu hỏi mẫu (bấm để thử ngay):")
            q_cols = st.columns(2)
            for idx, (short_title, full_prompt) in enumerate(QUICK_PROMPTS):
                with q_cols[idx % 2]:
                    if st.button(short_title, key=f"quick_prompt_{idx}", use_container_width=True, help=full_prompt):
                        st.session_state.queued_question = full_prompt
                        st.rerun()

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant" and msg.get("steps"):
                    with st.expander(
                        f"🔍 Quá trình suy luận & gọi công cụ ({len(msg['steps'])} bước)",
                        expanded=False,
                    ):
                        for s_line in msg["steps"]:
                            st.caption(s_line)
                st.write(msg["content"])

        if st.session_state.pending_interrupt:
            prev_interrupt = st.session_state.pending_interrupt
            st.info(f"🤖 **Agent cần thêm thông tin:** {prev_interrupt}")
            answer = st.chat_input("Nhập thông tin bổ sung cho agent...")
            if answer:
                st.session_state.messages.append({"role": "user", "content": answer})
                with st.chat_message("user"):
                    st.write(answer)
                st.session_state.pending_interrupt = None
                chat_ok = False
                with st.chat_message("assistant"):
                    steps_box = st.container()
                    steps_log: list[str] = []
                    try:
                        resp = requests.post(
                            f"{API_URL}/chat/resume",
                            json={"answer": answer, "thread_id": st.session_state.thread_id},
                            stream=True,
                            timeout=120,
                        )
                        if resp.status_code != 200:
                            st.error(_extract_api_error(resp))
                        else:
                            final_answer = _consume_stream(resp, steps_box, steps_log)
                            if final_answer:
                                st.write(final_answer)
                                st.session_state.messages.append(
                                    {"role": "assistant", "content": final_answer, "steps": steps_log}
                                )
                            chat_ok = True
                    except requests.RequestException as exc:
                        st.error(f"Không thể kết nối tới máy chủ API ({API_URL}): {exc}")
                if chat_ok:
                    st.rerun()
                else:
                    st.session_state.pending_interrupt = prev_interrupt
        else:
            typed_question = st.chat_input(
                "Hỏi về Luật Lao động Việt Nam (VD: thử việc, lương làm thêm, trợ cấp...)..."
            )
            question = typed_question or st.session_state.queued_question
            st.session_state.queued_question = None
            if question:
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.write(question)
                chat_ok = False
                with st.chat_message("assistant"):
                    steps_box = st.container()
                    steps_log = []
                    try:
                        resp = requests.post(
                            f"{API_URL}/chat",
                            json={"message": question, "thread_id": st.session_state.thread_id},
                            stream=True,
                            timeout=120,
                        )
                        if resp.status_code != 200:
                            st.error(_extract_api_error(resp))
                        else:
                            final_answer = _consume_stream(resp, steps_box, steps_log)
                            if final_answer:
                                st.write(final_answer)
                                st.session_state.messages.append(
                                    {"role": "assistant", "content": final_answer, "steps": steps_log}
                                )
                            chat_ok = True
                    except requests.RequestException as exc:
                        st.error(f"Không thể kết nối tới máy chủ API ({API_URL}): {exc}")
                if chat_ok:
                    st.rerun()

    with tab_contract:
        st.markdown(
            """<div class="rule-pills">
<span class="rule-pill">📋 Điều 21 BLLĐ: 9 Nội dung bắt buộc</span>
<span class="rule-pill">⏱️ Điều 25 BLLĐ: Giới hạn ngày thử việc</span>
<span class="rule-pill">💰 Điều 26 BLLĐ: Lương thử việc ≥ 85%</span>
<span class="rule-pill">🕒 Điều 105 BLLĐ: Giờ làm ≤ 8h/ngày, 48h/tuần</span>
<span class="rule-pill">🏛️ NĐ 293/2025: Lương tối thiểu vùng 2026</span>
</div>""",
            unsafe_allow_html=True,
        )

        sample_files = sorted(SAMPLE_CONTRACTS_DIR.glob("*.docx")) if SAMPLE_CONTRACTS_DIR.exists() else []
        source_mode = "upload"
        if sample_files:
            source_mode = st.radio(
                "Nguồn tệp hợp đồng:",
                options=["sample", "upload"],
                format_func=lambda m: (
                    "📁 Chọn hợp đồng mẫu có sẵn (Demo nhanh)"
                    if m == "sample"
                    else "📤 Tải tệp từ máy tính (.pdf, .docx)"
                ),
                horizontal=True,
            )

        active_filename: str | None = None
        active_bytes: bytes | None = None
        uploaded = None

        if source_mode == "upload":
            uploaded = st.file_uploader("Chọn file hợp đồng (.pdf hoặc .docx)", type=["pdf", "docx"])
            if uploaded is not None:
                active_filename = uploaded.name
                active_bytes = uploaded.getvalue()
        else:
            default_idx = next(
                (i for i, p in enumerate(sample_files) if p.name == "contract_09_nhieu_loi_1.docx"),
                0,
            )
            selected_sample = st.selectbox(
                "Chọn hợp đồng mẫu:",
                options=sample_files,
                index=default_idx,
                format_func=lambda p: f"{p.name} — {SAMPLE_CONTRACT_DESCRIPTIONS.get(p.name, 'Hợp đồng mẫu')}",
            )
            if selected_sample is not None:
                active_filename = selected_sample.name
                active_bytes = selected_sample.read_bytes()

        current_file_sig = (
            (source_mode, active_filename, len(active_bytes)) if (active_filename and active_bytes) else None
        )
        last_review = st.session_state.get("last_contract_review")
        if last_review and last_review.get("file_sig") != current_file_sig:
            st.session_state["last_contract_review"] = None

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            run_api_btn = bool(
                active_filename
                and active_bytes
                and st.button("🔍 Rà soát qua AI Agent API", type="primary", use_container_width=True)
            )
        with btn_col2:
            run_instant_btn = bool(
                source_mode == "sample"
                and active_filename
                and st.button(
                    "⚡ Xem ngay kết quả phân tích mẫu",
                    use_container_width=True,
                    help="Hiển thị ngay kết quả rà soát chuẩn đã kiểm chứng của hợp đồng mẫu này",
                )
            )

        if run_instant_btn and active_filename:
            instant_result = _build_offline_sample_review(active_filename)
            if instant_result:
                docx_bytes = export_contract_review_docx(
                    ContractInfo(**instant_result["extracted_info"]),
                    instant_result["warnings"],
                    source_filename=active_filename,
                )
                st.session_state["last_contract_review"] = {
                    "filename": active_filename,
                    "file_sig": current_file_sig,
                    "result": instant_result,
                    "docx_bytes": docx_bytes,
                }

        if run_api_btn and active_filename and active_bytes:
            resp = None
            with st.spinner("Đang trích xuất thông tin và đối chiếu các quy tắc pháp lý..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/review-contract",
                        files={"file": (active_filename, active_bytes)},
                        timeout=180,
                    )
                except requests.RequestException as exc:
                    st.error(f"Không thể kết nối tới máy chủ API ({API_URL}): {exc}")

            if resp is not None:
                if resp.status_code != 200:
                    st.error(_extract_api_error(resp))
                else:
                    result = resp.json()
                    docx_bytes = None
                    try:
                        export_resp = requests.post(
                            f"{API_URL}/review-contract/export-docx",
                            json={
                                "extracted_info": result["extracted_info"],
                                "warnings": result["warnings"],
                                "filename": active_filename,
                            },
                            timeout=60,
                        )
                        if export_resp.status_code == 200:
                            docx_bytes = export_resp.content
                    except requests.RequestException:
                        docx_bytes = None
                    if not docx_bytes:
                        docx_bytes = export_contract_review_docx(
                            ContractInfo(**result["extracted_info"]),
                            result["warnings"],
                            source_filename=active_filename,
                        )
                    st.session_state["last_contract_review"] = {
                        "filename": active_filename,
                        "file_sig": current_file_sig,
                        "result": result,
                        "docx_bytes": docx_bytes,
                    }

        if active_filename and st.session_state.get("last_contract_review"):
            review_state = st.session_state["last_contract_review"]
            result = review_state["result"]
            warnings = result["warnings"]
            extracted_info = result["extracted_info"]
            docx_bytes = review_state["docx_bytes"]

            st.divider()
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric(
                    "Kết quả tuân thủ",
                    "✅ Hợp lệ" if not warnings else f"⚠️ {len(warnings)} cảnh báo",
                    delta="Đạt chuẩn kiểm tra" if not warnings else "Cần chỉnh sửa điều khoản",
                    delta_color="normal" if not warnings else "inverse",
                )
            with m_col2:
                luong_val = (
                    f"{extracted_info['luong_chinh']:,.0f} đ".replace(",", ".")
                    if extracted_info.get("luong_chinh") is not None
                    else "Chưa rõ"
                )
                vung_sub = (
                    f"Vùng {extracted_info['vung_luong_toi_thieu']}"
                    if extracted_info.get("vung_luong_toi_thieu")
                    else "Chưa rõ vùng"
                )
                st.metric("Mức lương chính thức", luong_val, delta=vung_sub, delta_color="off")
            with m_col3:
                tv_val = (
                    f"{extracted_info['so_ngay_thu_viec']} ngày"
                    if extracted_info.get("so_ngay_thu_viec") is not None
                    else "Không thử việc / Chưa rõ"
                )
                gio_ngay_val = (
                    f"{extracted_info['gio_lam_ngay']:g}"
                    if extracted_info.get("gio_lam_ngay") is not None
                    else "?"
                )
                gio_tuan_val = (
                    f"{extracted_info['gio_lam_tuan']:g}"
                    if extracted_info.get("gio_lam_tuan") is not None
                    else "?"
                )
                gio_sub = f"{gio_ngay_val}h/ngày · {gio_tuan_val}h/tuần"
                st.metric("Thử việc & Thời giờ làm việc", tv_val, delta=gio_sub, delta_color="off")

            if not warnings:
                st.success(
                    "✅ Không phát hiện điều khoản vi phạm theo các quy tắc kiểm tra hiện hành "
                    "(Điều 21, 25, 26, 105 BLLĐ 2019 và Nghị định 293/2025/NĐ-CP)."
                )
            else:
                st.warning(f"Phát hiện **{len(warnings)}** điều khoản có dấu hiệu vi phạm:")
                for idx, w in enumerate(warnings, start=1):
                    with st.expander(f"⚠️ Cảnh báo #{idx}: {w['canh_bao']}", expanded=True):
                        st.markdown(f"**📌 Căn cứ pháp lý:** `{w['can_cu']}`")
                        trich_dan = w.get("trich_dan", "")
                        if trich_dan:
                            st.caption("Trích dẫn điều luật:")
                            st.text(trich_dan)

            general_rows, checklist = format_extracted_contract_summary(extracted_info)
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.markdown("##### 📋 Thông tin trích xuất từ hợp đồng")
                for label, val in general_rows:
                    st.markdown(f"- **{label}:** {val}")
            with info_col2:
                passed_count = sum(1 for _, ok in checklist if ok)
                st.markdown(f"##### ☑️ Nội dung bắt buộc theo Điều 21 ({passed_count}/{len(checklist)})")
                st.progress(passed_count / len(checklist) if checklist else 1.0)
                for label, ok in checklist:
                    icon = "✅" if ok else "❌"
                    st.markdown(f"{icon} {label}")

            with st.expander("🔧 Xem dữ liệu JSON trích xuất gốc"):
                st.json(extracted_info)

            st.download_button(
                label="📥 Tải báo cáo rà soát (.docx)",
                data=docx_bytes,
                file_name=f"bao_cao_ra_soat_{Path(active_filename).stem}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
            )


if __name__ == "__main__" or _is_running_in_streamlit():
    render_app()
