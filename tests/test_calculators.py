import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.tools.calculators import (
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
