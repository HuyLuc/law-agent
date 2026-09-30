"""Ra soat hop dong lao dong: doc PDF/DOCX, LLM trich thong tin co cau truc,
roi KIEM TRA BANG QUY TAC LAP TRINH SAN (khong de LLM tu danh gia dung/sai).

Xem PLAN.md Tuan 4 Buoi 3-4.
"""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from src.llm import build_llm_chain, structured_output_transform
from src.tools.legal_lookup import get_article

TrinhDo = Literal["quan_ly", "cao_dang_tro_len", "trung_cap", "khac"]
Vung = Literal["I", "II", "III", "IV"]

# Nghi dinh 293/2025/ND-CP Dieu 3 (luong toi thieu vung, hieu luc 01/01/2026)
LUONG_TOI_THIEU_VUNG = {"I": 5_310_000, "II": 4_730_000, "III": 4_140_000, "IV": 3_700_000}

# Dieu 25 BLLD 2019: gioi han thu viec theo trinh do
GIOI_HAN_THU_VIEC_NGAY = {"quan_ly": 180, "cao_dang_tro_len": 60, "trung_cap": 30, "khac": 6}


class ContractInfo(BaseModel):
    loai_hop_dong: Literal["khong_xac_dinh_thoi_han", "xac_dinh_thoi_han"] | None = None
    thoi_han_hop_dong_thang: int | None = None
    vi_tri_cong_viec: str | None = None
    trinh_do_yeu_cau: TrinhDo | None = Field(
        default=None,
        description=(
            "Muc trinh do cua vi tri cong viec: 'quan_ly' (nguoi quan ly doanh nghiep), "
            "'cao_dang_tro_len', 'trung_cap' (trung cap/cong nhan ky thuat/nhan vien nghiep vu), "
            "'khac' (cong viec pho thong khong yeu cau bang cap)"
        ),
    )
    so_ngay_thu_viec: int | None = None
    luong_thu_viec: float | None = Field(default=None, description="Luong trong thoi gian thu viec (dong/thang)")
    luong_chinh: float | None = Field(default=None, description="Muc luong chinh thuc sau thu viec (dong/thang)")
    vung_luong_toi_thieu: Vung | None = Field(
        default=None, description="Vung luong toi thieu neu hop dong co ghi ro (I/II/III/IV); None neu khong ro"
    )
    gio_lam_ngay: float | None = Field(default=None, description="So gio lam viec binh thuong moi ngay")
    gio_lam_tuan: float | None = Field(default=None, description="So gio lam viec binh thuong moi tuan")

    co_thong_tin_cac_ben: bool = Field(default=True, description="HDLD co ghi ten/dia chi cac ben khong")
    co_cong_viec_dia_diem: bool = Field(default=True, description="HDLD co ghi ro cong viec va dia diem lam viec khong")
    co_thoi_han: bool = Field(default=True, description="HDLD co ghi ro thoi han hop dong khong")
    co_muc_luong: bool = Field(default=True, description="HDLD co ghi ro muc luong, hinh thuc, thoi han tra luong khong")
    co_che_do_nang_luong: bool = Field(default=True, description="HDLD co ghi che do nang bac, nang luong khong")
    co_thoi_gio_lam_viec_nghi_ngoi: bool = Field(default=True, description="HDLD co ghi thoi gio lam viec, nghi ngoi khong")
    co_trang_bi_bao_ho: bool = Field(default=True, description="HDLD co ghi trang bi bao ho lao dong khong")
    co_bhxh: bool = Field(default=True, description="HDLD co ghi BHXH/BHYT/BHTN khong")
    co_dao_tao: bool = Field(default=True, description="HDLD co ghi dao tao, boi duong nang cao trinh do ky nang nghe khong")


EXTRACTION_PROMPT = """Doc noi dung hop dong lao dong duoi day va trich xuat thong tin theo dung cau truc
yeu cau. Neu khong tim thay thong tin nao do trong hop dong, de None (rieng cac truong bat dau
bang "co_" thi tra loi false neu khong thay).

--- NOI DUNG HOP DONG ---
{text}
"""


def extract_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        from docx import Document

        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError(f"Không hỗ trợ định dạng {suffix}, chỉ hỗ trợ .pdf và .docx")


def extract_contract_info(text: str) -> ContractInfo:
    llm = build_llm_chain(structured_output_transform(ContractInfo))
    return llm.invoke(EXTRACTION_PROMPT.format(text=text))


def _quote_article(van_ban: str, dieu: int) -> str:
    chunks = get_article(van_ban, dieu)
    if not chunks:
        return ""
    return chunks[0]["noi_dung"]


def check_thoi_gian_thu_viec(info: ContractInfo) -> list[dict]:
    if info.so_ngay_thu_viec is None or info.trinh_do_yeu_cau is None:
        return []
    limit = GIOI_HAN_THU_VIEC_NGAY[info.trinh_do_yeu_cau]
    if info.so_ngay_thu_viec <= limit:
        return []
    return [
        {
            "quy_tac": "thoi_gian_thu_viec",
            "canh_bao": (
                f"Thời gian thử việc {info.so_ngay_thu_viec} ngày vượt quá mức tối đa cho phép "
                f"({limit} ngày) đối với vị trí này."
            ),
            "can_cu": "Điều 25 Bộ luật Lao động 2019",
            "trich_dan": _quote_article("Bộ luật Lao động 2019", 25),
        }
    ]


def check_luong_thu_viec(info: ContractInfo) -> list[dict]:
    if info.luong_thu_viec is None or info.luong_chinh is None:
        return []
    muc_toi_thieu = 0.85 * info.luong_chinh
    if info.luong_thu_viec >= muc_toi_thieu:
        return []
    return [
        {
            "quy_tac": "luong_thu_viec",
            "canh_bao": (
                f"Lương thử việc {info.luong_thu_viec:,.0f}đ thấp hơn mức tối thiểu 85% lương chính "
                f"({muc_toi_thieu:,.0f}đ)."
            ),
            "can_cu": "Điều 26 Bộ luật Lao động 2019",
            "trich_dan": _quote_article("Bộ luật Lao động 2019", 26),
        }
    ]


def check_luong_toi_thieu_vung(info: ContractInfo) -> list[dict]:
    if info.luong_chinh is None or info.vung_luong_toi_thieu is None:
        return []
    muc_toi_thieu = LUONG_TOI_THIEU_VUNG[info.vung_luong_toi_thieu]
    if info.luong_chinh >= muc_toi_thieu:
        return []
    return [
        {
            "quy_tac": "luong_toi_thieu_vung",
            "canh_bao": (
                f"Lương chính {info.luong_chinh:,.0f}đ thấp hơn mức lương tối thiểu Vùng "
                f"{info.vung_luong_toi_thieu} ({muc_toi_thieu:,.0f}đ)."
            ),
            "can_cu": "Điều 3 Nghị định 293/2025/NĐ-CP",
            "trich_dan": _quote_article("293/2025/NĐ-CP", 3),
        }
    ]


def check_gio_lam_viec(info: ContractInfo) -> list[dict]:
    warnings = []
    if info.gio_lam_ngay is not None and info.gio_lam_ngay > 8:
        warnings.append(
            {
                "quy_tac": "gio_lam_ngay",
                "canh_bao": f"Giờ làm việc {info.gio_lam_ngay} giờ/ngày vượt quá 8 giờ/ngày.",
                "can_cu": "Điều 105 Bộ luật Lao động 2019",
                "trich_dan": _quote_article("Bộ luật Lao động 2019", 105),
            }
        )
    if info.gio_lam_tuan is not None and info.gio_lam_tuan > 48:
        warnings.append(
            {
                "quy_tac": "gio_lam_tuan",
                "canh_bao": f"Giờ làm việc {info.gio_lam_tuan} giờ/tuần vượt quá 48 giờ/tuần.",
                "can_cu": "Điều 105 Bộ luật Lao động 2019",
                "trich_dan": _quote_article("Bộ luật Lao động 2019", 105),
            }
        )
    return warnings


_NOI_DUNG_BAT_BUOC = [
    ("co_thong_tin_cac_ben", "tên/địa chỉ các bên"),
    ("co_cong_viec_dia_diem", "công việc và địa điểm làm việc"),
    ("co_thoi_han", "thời hạn hợp đồng"),
    ("co_muc_luong", "mức lương, hình thức và thời hạn trả lương"),
    ("co_che_do_nang_luong", "chế độ nâng bậc, nâng lương"),
    ("co_thoi_gio_lam_viec_nghi_ngoi", "thời giờ làm việc, thời giờ nghỉ ngơi"),
    ("co_trang_bi_bao_ho", "trang bị bảo hộ lao động"),
    ("co_bhxh", "bảo hiểm xã hội, bảo hiểm y tế, bảo hiểm thất nghiệp"),
    ("co_dao_tao", "đào tạo, bồi dưỡng, nâng cao trình độ, kỹ năng nghề"),
]


def check_noi_dung_bat_buoc(info: ContractInfo) -> list[dict]:
    missing = [ten for field, ten in _NOI_DUNG_BAT_BUOC if not getattr(info, field)]
    if not missing:
        return []
    return [
        {
            "quy_tac": "noi_dung_bat_buoc",
            "canh_bao": "Hợp đồng thiếu nội dung bắt buộc: " + "; ".join(missing) + ".",
            "can_cu": "Điều 21 Bộ luật Lao động 2019",
            "trich_dan": _quote_article("Bộ luật Lao động 2019", 21),
        }
    ]


ALL_CHECKS = [
    check_thoi_gian_thu_viec,
    check_luong_thu_viec,
    check_luong_toi_thieu_vung,
    check_gio_lam_viec,
    check_noi_dung_bat_buoc,
]


def check_contract(info: ContractInfo) -> list[dict]:
    warnings = []
    for check in ALL_CHECKS:
        warnings.extend(check(info))
    return warnings


def review_contract_file(path: Path) -> tuple[ContractInfo, list[dict]]:
    text = extract_text_from_file(path)
    info = extract_contract_info(text)
    return info, check_contract(info)
