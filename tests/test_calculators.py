import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.tools.calculators import (
    tinh_boi_thuong_cham_dut_trai_luat,
    tinh_ngay_phep_nam,
    tinh_thoi_han_bao_truoc,
    tinh_tien_lam_them_gio,
    tinh_tro_cap_mat_viec,
    tinh_tro_cap_thoi_viec,
)

CALC_PATH = Path(__file__).resolve().parents[1] / "data" / "eval" / "calc.jsonl"

FUNCS = {
    "tinh_tro_cap_thoi_viec": tinh_tro_cap_thoi_viec,
    "tinh_tro_cap_mat_viec": tinh_tro_cap_mat_viec,
    "tinh_tien_lam_them_gio": tinh_tien_lam_them_gio,
    "tinh_ngay_phep_nam": tinh_ngay_phep_nam,
    "tinh_thoi_han_bao_truoc": tinh_thoi_han_bao_truoc,
}

# tien (dong): sai lech <= 1000d theo PLAN.md muc 7.3; so ngay: gan bang tuyet doi
CURRENCY_TOOLS = {"tinh_tro_cap_thoi_viec", "tinh_tro_cap_mat_viec", "tinh_tien_lam_them_gio"}


def _load_calc_set() -> list[dict]:
    return [json.loads(line) for line in CALC_PATH.open(encoding="utf-8")]


@pytest.mark.parametrize("case", _load_calc_set(), ids=lambda c: c["id"])
def test_calc_jsonl_matches_expected(case):
    fn = FUNCS[case["tool"]]
    result = fn(**case["input"])
    tolerance = 1000 if case["tool"] in CURRENCY_TOOLS else 0.01
    assert abs(result["ket_qua"] - case["expected"]) <= tolerance, (
        f"{case['id']}: got {result['ket_qua']}, expected {case['expected']}"
    )
    assert result["cach_tinh"]
    assert result["can_cu"]


def test_all_40_cases_present():
    cases = _load_calc_set()
    assert len(cases) == 40
    counts: dict[str, int] = {}
    for c in cases:
        counts[c["tool"]] = counts.get(c["tool"], 0) + 1
    assert counts == dict.fromkeys(FUNCS, 8)


def test_tro_cap_thoi_viec_rejects_negative_salary():
    with pytest.raises(ValidationError):
        tinh_tro_cap_thoi_viec(
            thoi_gian_lam_viec_thang=24, thoi_gian_dong_bhtn_thang=0, luong_bq_6_thang=-1
        )


def test_tro_cap_thoi_viec_rejects_negative_months():
    with pytest.raises(ValidationError):
        tinh_tro_cap_thoi_viec(
            thoi_gian_lam_viec_thang=-5, thoi_gian_dong_bhtn_thang=0, luong_bq_6_thang=10_000_000
        )


def test_tro_cap_thoi_viec_rejects_bhtn_exceeding_total_time():
    with pytest.raises(ValidationError):
        tinh_tro_cap_thoi_viec(
            thoi_gian_lam_viec_thang=12, thoi_gian_dong_bhtn_thang=24, luong_bq_6_thang=10_000_000
        )


def test_lam_them_gio_rejects_invalid_loai_ngay():
    with pytest.raises(ValidationError):
        tinh_tien_lam_them_gio(don_gia_gio=50_000, loai_ngay="khong_hop_le", so_gio=2, lam_dem=False)


def test_lam_them_gio_rejects_negative_gio():
    with pytest.raises(ValidationError):
        tinh_tien_lam_them_gio(don_gia_gio=50_000, loai_ngay="thuong", so_gio=-1, lam_dem=False)


def test_ngay_phep_nam_rejects_thang_ngoai_khoang():
    with pytest.raises(ValidationError):
        tinh_ngay_phep_nam(loai_lao_dong="binh_thuong", so_thang_lam_viec=13, tham_nien_nam=0)


def test_thoi_han_bao_truoc_rejects_am():
    with pytest.raises(ValidationError):
        tinh_thoi_han_bao_truoc(thoi_han_hop_dong_thang=-1)


def test_boi_thuong_cham_dut_trai_luat_standard():
    # Luong 10tr, 3 thang khong lam viec (30tr), boi thuong them 2 thang (20tr),
    # lam viec 36 thang, BHTN 12 thang -> 24 thang = 2 nam -> TCTV = 2 * 0.5 * 10tr = 10tr
    # Tong = 30tr + 20tr + 10tr = 60tr
    res = tinh_boi_thuong_cham_dut_trai_luat(
        luong_thang=10_000_000,
        so_thang_khong_duoc_lam_viec=3,
        thoi_gian_lam_viec_thang=36,
        thoi_gian_dong_bhtn_thang=12,
    )
    assert res["ket_qua"] == 60_000_000
    assert "Điều 41 Bộ luật Lao động 2019" in res["can_cu"]
    assert "Điều 46 Bộ luật Lao động 2019" in res["can_cu"]
    assert res["cach_tinh"]


def test_boi_thuong_cham_dut_trai_luat_with_notice_violation():
    # Luong 13tr (13tr / 26 = 500k/ngay), vi pham 10 ngay = 5tr
    # 2 thang khong lam viec (26tr) + 2 thang boi thuong them (26tr)
    # Lam viec 24 thang, BHTN 24 thang -> TCTV = 0
    # Tong = 26tr + 26tr + 0 + 5tr = 57tr
    res = tinh_boi_thuong_cham_dut_trai_luat(
        luong_thang=13_000_000,
        so_thang_khong_duoc_lam_viec=2,
        thoi_gian_lam_viec_thang=24,
        thoi_gian_dong_bhtn_thang=24,
        so_ngay_vi_pham_bao_truoc=10,
    )
    assert res["ket_qua"] == 57_000_000
    assert "26 ngày công" in res["cach_tinh"]
    assert "Điều 36 Bộ luật Lao động 2019" in res["can_cu"]


def test_boi_thuong_cham_dut_trai_luat_under_12_months():
    # Lam viec 8 thang (< 12 thang) -> khong co tro cap thoi viec (0d)
    # 1 thang khong lam viec (10tr) + 2 thang boi thuong them (20tr) = 30tr
    res = tinh_boi_thuong_cham_dut_trai_luat(
        luong_thang=10_000_000,
        so_thang_khong_duoc_lam_viec=1,
        thoi_gian_lam_viec_thang=8,
        thoi_gian_dong_bhtn_thang=0,
    )
    assert res["ket_qua"] == 30_000_000
    assert "dưới 12 tháng" in res["cach_tinh"]


def test_boi_thuong_cham_dut_trai_luat_zero_months_worked():
    # Moi di lam chua du 1 thang (0 thang) da bi sa thai trai luat
    res = tinh_boi_thuong_cham_dut_trai_luat(
        luong_thang=10_000_000,
        so_thang_khong_duoc_lam_viec=1,
        thoi_gian_lam_viec_thang=0,
        thoi_gian_dong_bhtn_thang=0,
    )
    assert res["ket_qua"] == 30_000_000
    assert "dưới 12 tháng" in res["cach_tinh"]


def test_boi_thuong_cham_dut_trai_luat_rejects_negative_salary():
    with pytest.raises(ValidationError):
        tinh_boi_thuong_cham_dut_trai_luat(
            luong_thang=-10_000_000,
            so_thang_khong_duoc_lam_viec=2,
            thoi_gian_lam_viec_thang=24,
            thoi_gian_dong_bhtn_thang=12,
        )


def test_boi_thuong_cham_dut_trai_luat_rejects_extra_months_less_than_2():
    with pytest.raises(ValidationError):
        tinh_boi_thuong_cham_dut_trai_luat(
            luong_thang=10_000_000,
            so_thang_khong_duoc_lam_viec=2,
            thoi_gian_lam_viec_thang=24,
            thoi_gian_dong_bhtn_thang=12,
            so_thang_boi_thuong_them=1,
        )


def test_boi_thuong_cham_dut_trai_luat_rejects_bhtn_exceeding_total_time():
    with pytest.raises(ValidationError):
        tinh_boi_thuong_cham_dut_trai_luat(
            luong_thang=10_000_000,
            so_thang_khong_duoc_lam_viec=2,
            thoi_gian_lam_viec_thang=12,
            thoi_gian_dong_bhtn_thang=24,
        )

