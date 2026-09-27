"""5 ham tinh toan thuan Python (khong goi LLM) cho agent.

Doi chieu cong thuc voi BLLD2019 va ND145/2020 (xem PLAN.md muc "Tuan 3,
Buoi 1"). Moi ham nhan input da duoc kiem tra bang Pydantic va tra ve:
{"ket_qua": ..., "cach_tinh": "...", "can_cu": [...]}.
"""

import math
from typing import Literal

from pydantic import BaseModel, Field, model_validator


def _format_vnd(amount: float) -> str:
    return f"{amount:,.0f}đ".replace(",", ".")


def _effective_years(thang_lam_viec: int, thang_da_dong_bhtn: int) -> tuple[float, str]:
    """Quy tac lam tron cua ND145/2020 Dieu 8 khoan 3 diem c."""
    effective_months = thang_lam_viec - thang_da_dong_bhtn
    full_years, remainder = divmod(effective_months, 12)
    if remainder == 0:
        years = float(full_years)
        note = f"{effective_months} tháng = {full_years} năm tròn"
    elif remainder <= 6:
        years = full_years + 0.5
        note = f"{effective_months} tháng = {full_years} năm + {remainder} tháng lẻ (≤6 tháng → +0.5 năm)"
    else:
        years = full_years + 1.0
        note = f"{effective_months} tháng = {full_years} năm + {remainder} tháng lẻ (>6 tháng → +1 năm)"
    return years, note


# ---------------------------------------------------------------------------
# tinh_tro_cap_thoi_viec


class TroCapThoiViecInput(BaseModel):
    thoi_gian_lam_viec_thang: int = Field(gt=0, description="Tong thoi gian lam viec thuc te (thang)")
    thoi_gian_dong_bhtn_thang: int = Field(ge=0, description="Thoi gian da tham gia BHTN (thang)")
    luong_bq_6_thang: float = Field(gt=0, description="Luong binh quan 6 thang lien ke (dong)")

    @model_validator(mode="after")
    def _check_bhtn_khong_vuot_qua_tong_thoi_gian(self) -> "TroCapThoiViecInput":
        if self.thoi_gian_dong_bhtn_thang > self.thoi_gian_lam_viec_thang:
            raise ValueError(
                "thoi_gian_dong_bhtn_thang khong the lon hon thoi_gian_lam_viec_thang"
            )
        return self


def tinh_tro_cap_thoi_viec(
    thoi_gian_lam_viec_thang: int, thoi_gian_dong_bhtn_thang: int, luong_bq_6_thang: float
) -> dict:
    data = TroCapThoiViecInput(
        thoi_gian_lam_viec_thang=thoi_gian_lam_viec_thang,
        thoi_gian_dong_bhtn_thang=thoi_gian_dong_bhtn_thang,
        luong_bq_6_thang=luong_bq_6_thang,
    )
    years, note = _effective_years(data.thoi_gian_lam_viec_thang, data.thoi_gian_dong_bhtn_thang)
    ket_qua = round(years * 0.5 * data.luong_bq_6_thang)
    return {
        "ket_qua": ket_qua,
        "cach_tinh": (
            f"{note}. Trợ cấp = {years} năm × 0.5 tháng × {_format_vnd(data.luong_bq_6_thang)} "
            f"= {_format_vnd(ket_qua)}"
        ),
        "can_cu": ["Điều 46 Bộ luật Lao động 2019", "Điều 8 Nghị định 145/2020/NĐ-CP"],
    }


# ---------------------------------------------------------------------------
# tinh_tro_cap_mat_viec


class TroCapMatViecInput(BaseModel):
    thoi_gian_lam_viec_thang: int = Field(gt=0)
    thoi_gian_dong_bhtn_thang: int = Field(ge=0)
    luong_bq_6_thang: float = Field(gt=0)

    @model_validator(mode="after")
    def _check_bhtn_khong_vuot_qua_tong_thoi_gian(self) -> "TroCapMatViecInput":
        if self.thoi_gian_dong_bhtn_thang > self.thoi_gian_lam_viec_thang:
            raise ValueError(
                "thoi_gian_dong_bhtn_thang khong the lon hon thoi_gian_lam_viec_thang"
            )
        return self


def tinh_tro_cap_mat_viec(
    thoi_gian_lam_viec_thang: int, thoi_gian_dong_bhtn_thang: int, luong_bq_6_thang: float
) -> dict:
    data = TroCapMatViecInput(
        thoi_gian_lam_viec_thang=thoi_gian_lam_viec_thang,
        thoi_gian_dong_bhtn_thang=thoi_gian_dong_bhtn_thang,
        luong_bq_6_thang=luong_bq_6_thang,
    )
    years, note = _effective_years(data.thoi_gian_lam_viec_thang, data.thoi_gian_dong_bhtn_thang)
    tinh_theo_nam = years * data.luong_bq_6_thang
    muc_toi_thieu = 2 * data.luong_bq_6_thang
    ket_qua = round(max(tinh_theo_nam, muc_toi_thieu))
    dung_muc_toi_thieu = muc_toi_thieu > tinh_theo_nam
    cach_tinh = (
        f"{note}. Trợ cấp = {years} năm × 1 tháng × {_format_vnd(data.luong_bq_6_thang)} = "
        f"{_format_vnd(tinh_theo_nam)}"
    )
    if dung_muc_toi_thieu:
        cach_tinh += f", thấp hơn mức tối thiểu 2 tháng lương ({_format_vnd(muc_toi_thieu)}) nên áp dụng mức tối thiểu"
    return {
        "ket_qua": ket_qua,
        "cach_tinh": cach_tinh,
        "can_cu": ["Điều 47 Bộ luật Lao động 2019", "Điều 8 Nghị định 145/2020/NĐ-CP"],
    }


# ---------------------------------------------------------------------------
# tinh_tien_lam_them_gio

LoaiNgay = Literal["thuong", "nghi_tuan", "le_tet"]

_MULTIPLIER = {"thuong": 1.5, "nghi_tuan": 2.0, "le_tet": 3.0}
_TEN_LOAI_NGAY = {"thuong": "ngày thường", "nghi_tuan": "ngày nghỉ hằng tuần", "le_tet": "ngày nghỉ lễ, tết"}


class LamThemGioInput(BaseModel):
    don_gia_gio: float = Field(gt=0, description="Don gia tien luong theo gio (dong)")
    loai_ngay: LoaiNgay
    so_gio: float = Field(gt=0)
    lam_dem: bool = False


def tinh_tien_lam_them_gio(
    don_gia_gio: float, loai_ngay: str, so_gio: float, lam_dem: bool
) -> dict:
    data = LamThemGioInput(
        don_gia_gio=don_gia_gio, loai_ngay=loai_ngay, so_gio=so_gio, lam_dem=lam_dem
    )
    multiplier = _MULTIPLIER[data.loai_ngay]
    cach_tinh = (
        f"{data.so_gio} giờ × {_format_vnd(data.don_gia_gio)} × {int(multiplier * 100)}% "
        f"({_TEN_LOAI_NGAY[data.loai_ngay]}, Điều 98 khoản 1)"
    )
    if data.lam_dem:
        multiplier += 0.3 + 0.2
        cach_tinh += " + 30% làm đêm (khoản 2) + 20% làm thêm giờ vào ban đêm (khoản 3)"
    ket_qua = round(data.so_gio * data.don_gia_gio * multiplier)
    cach_tinh += f" = {_format_vnd(ket_qua)}"
    return {
        "ket_qua": ket_qua,
        "cach_tinh": cach_tinh,
        "can_cu": ["Điều 98 Bộ luật Lao động 2019"],
    }


# ---------------------------------------------------------------------------
# tinh_ngay_phep_nam

LoaiLaoDong = Literal["binh_thuong", "nang_nhoc", "dac_biet_nang_nhoc"]

_NGAY_PHEP_CO_BAN = {"binh_thuong": 12, "nang_nhoc": 14, "dac_biet_nang_nhoc": 16}


class NgayPhepNamInput(BaseModel):
    loai_lao_dong: LoaiLaoDong
    so_thang_lam_viec: int = Field(gt=0, le=12, description="So thang da lam trong nam (toi da 12)")
    tham_nien_nam: int = Field(ge=0)


def tinh_ngay_phep_nam(
    loai_lao_dong: str, so_thang_lam_viec: int, tham_nien_nam: int
) -> dict:
    data = NgayPhepNamInput(
        loai_lao_dong=loai_lao_dong,
        so_thang_lam_viec=so_thang_lam_viec,
        tham_nien_nam=tham_nien_nam,
    )
    base = _NGAY_PHEP_CO_BAN[data.loai_lao_dong]
    if data.so_thang_lam_viec < 12:
        ket_qua = round(base * data.so_thang_lam_viec / 12, 2)
        cach_tinh = (
            f"Chưa làm đủ 12 tháng: {base} ngày × {data.so_thang_lam_viec}/12 tháng = {ket_qua} ngày"
        )
    else:
        cong_them = math.floor(data.tham_nien_nam / 5)
        ket_qua = base + cong_them
        cach_tinh = f"{base} ngày cơ bản"
        if cong_them:
            cach_tinh += f" + {cong_them} ngày thâm niên ({data.tham_nien_nam} năm, cứ 5 năm +1 ngày)"
        cach_tinh += f" = {ket_qua} ngày"
    return {
        "ket_qua": ket_qua,
        "cach_tinh": cach_tinh,
        "can_cu": ["Điều 113 Bộ luật Lao động 2019", "Điều 114 Bộ luật Lao động 2019"],
    }


# ---------------------------------------------------------------------------
# tinh_thoi_han_bao_truoc


class ThoiHanBaoTruocInput(BaseModel):
    thoi_han_hop_dong_thang: int | None = Field(
        default=None, ge=0, description="So thang thoi han HDLD; None = khong xac dinh thoi han"
    )


def tinh_thoi_han_bao_truoc(thoi_han_hop_dong_thang: int | None) -> dict:
    data = ThoiHanBaoTruocInput(thoi_han_hop_dong_thang=thoi_han_hop_dong_thang)
    if data.thoi_han_hop_dong_thang is None:
        return {
            "ket_qua": 45,
            "cach_tinh": "Hợp đồng không xác định thời hạn → báo trước ít nhất 45 ngày",
            "can_cu": ["Điều 35 Bộ luật Lao động 2019", "Điều 36 Bộ luật Lao động 2019"],
        }
    if 12 <= data.thoi_han_hop_dong_thang <= 36:
        return {
            "ket_qua": 30,
            "cach_tinh": (
                f"Hợp đồng xác định thời hạn {data.thoi_han_hop_dong_thang} tháng (12-36 tháng) "
                "→ báo trước ít nhất 30 ngày"
            ),
            "can_cu": ["Điều 35 Bộ luật Lao động 2019", "Điều 36 Bộ luật Lao động 2019"],
        }
    return {
        "ket_qua": 3,
        "cach_tinh": (
            f"Hợp đồng xác định thời hạn {data.thoi_han_hop_dong_thang} tháng (dưới 12 tháng) "
            "→ báo trước ít nhất 3 ngày làm việc"
        ),
        "can_cu": ["Điều 35 Bộ luật Lao động 2019", "Điều 36 Bộ luật Lao động 2019"],
    }
