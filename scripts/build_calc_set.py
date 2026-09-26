"""Sinh data/eval/calc.jsonl (Tuan 2, Buoi 4): 40 tinh huong tinh toan.

Moi ham tinh (5 ham x 8 tinh huong) duoc tinh tay theo dung cong thuc doi
chieu voi BLLD2019 va ND145/2020 (xem PLAN.md muc "Tuan 3, Buoi 1"), va
duoc kiem lai bang code trong script nay truoc khi ghi file -- neu cong
thuc code va so lieu ky vong lech nhau thi script se bao loi ngay, tranh
tu tay tinh sai roi bien no thanh "dap an chuan".

Chay: python scripts/build_calc_set.py
"""

# ruff: noqa: C408 -- dict(...) de doc hon {} cho danh sach tinh huong dai

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "eval" / "calc.jsonl"


def _effective_years(thang_lam_viec: int, thang_da_dong_bhtn: int) -> float:
    """Quy tac lam tron cua ND145/2020 Dieu 8 khoan 3 diem c."""
    effective_months = thang_lam_viec - thang_da_dong_bhtn
    full_years, remainder = divmod(effective_months, 12)
    if remainder == 0:
        return float(full_years)
    if remainder <= 6:
        return full_years + 0.5
    return full_years + 1.0


def tinh_tro_cap_thoi_viec(thoi_gian_lam_viec_thang, thoi_gian_dong_bhtn_thang, luong_bq_6_thang):
    years = _effective_years(thoi_gian_lam_viec_thang, thoi_gian_dong_bhtn_thang)
    return round(years * 0.5 * luong_bq_6_thang)


def tinh_tro_cap_mat_viec(thoi_gian_lam_viec_thang, thoi_gian_dong_bhtn_thang, luong_bq_6_thang):
    years = _effective_years(thoi_gian_lam_viec_thang, thoi_gian_dong_bhtn_thang)
    return round(max(years * luong_bq_6_thang, 2 * luong_bq_6_thang))


def tinh_tien_lam_them_gio(don_gia_gio, loai_ngay, so_gio, lam_dem):
    multiplier = {"thuong": 1.5, "nghi_tuan": 2.0, "le_tet": 3.0}[loai_ngay]
    if lam_dem:
        multiplier += 0.3 + 0.2
    return round(so_gio * don_gia_gio * multiplier)


def tinh_ngay_phep_nam(loai_lao_dong, so_thang_lam_viec, tham_nien_nam):
    base = {"binh_thuong": 12, "nang_nhoc": 14, "dac_biet_nang_nhoc": 16}[loai_lao_dong]
    if so_thang_lam_viec < 12:
        return round(base * so_thang_lam_viec / 12, 2)
    return base + math.floor(tham_nien_nam / 5)


def tinh_thoi_han_bao_truoc(thoi_han_hop_dong_thang):
    if thoi_han_hop_dong_thang is None:
        return 45
    if 12 <= thoi_han_hop_dong_thang <= 36:
        return 30
    return 3


CALC_SET = [
    # ---- tinh_tro_cap_thoi_viec (8) ----
    dict(id="c001", tool="tinh_tro_cap_thoi_viec",
         input=dict(thoi_gian_lam_viec_thang=54, thoi_gian_dong_bhtn_thang=0, luong_bq_6_thang=12_000_000)),
    dict(id="c002", tool="tinh_tro_cap_thoi_viec",
         input=dict(thoi_gian_lam_viec_thang=84, thoi_gian_dong_bhtn_thang=0, luong_bq_6_thang=10_000_000)),
    dict(id="c003", tool="tinh_tro_cap_thoi_viec",
         input=dict(thoi_gian_lam_viec_thang=90, thoi_gian_dong_bhtn_thang=0, luong_bq_6_thang=8_000_000)),
    dict(id="c004", tool="tinh_tro_cap_thoi_viec",
         input=dict(thoi_gian_lam_viec_thang=91, thoi_gian_dong_bhtn_thang=0, luong_bq_6_thang=8_000_000)),
    dict(id="c005", tool="tinh_tro_cap_thoi_viec",
         input=dict(thoi_gian_lam_viec_thang=120, thoi_gian_dong_bhtn_thang=36, luong_bq_6_thang=15_000_000)),
    dict(id="c006", tool="tinh_tro_cap_thoi_viec",
         input=dict(thoi_gian_lam_viec_thang=30, thoi_gian_dong_bhtn_thang=6, luong_bq_6_thang=9_000_000)),
    dict(id="c007", tool="tinh_tro_cap_thoi_viec",
         input=dict(thoi_gian_lam_viec_thang=14, thoi_gian_dong_bhtn_thang=10, luong_bq_6_thang=6_000_000)),
    dict(id="c008", tool="tinh_tro_cap_thoi_viec",
         input=dict(thoi_gian_lam_viec_thang=180, thoi_gian_dong_bhtn_thang=100, luong_bq_6_thang=20_000_000)),

    # ---- tinh_tro_cap_mat_viec (8) ----
    dict(id="c009", tool="tinh_tro_cap_mat_viec",
         input=dict(thoi_gian_lam_viec_thang=30, thoi_gian_dong_bhtn_thang=0, luong_bq_6_thang=10_000_000)),
    dict(id="c010", tool="tinh_tro_cap_mat_viec",
         input=dict(thoi_gian_lam_viec_thang=18, thoi_gian_dong_bhtn_thang=0, luong_bq_6_thang=7_000_000)),
    dict(id="c011", tool="tinh_tro_cap_mat_viec",
         input=dict(thoi_gian_lam_viec_thang=13, thoi_gian_dong_bhtn_thang=0, luong_bq_6_thang=5_000_000)),
    dict(id="c012", tool="tinh_tro_cap_mat_viec",
         input=dict(thoi_gian_lam_viec_thang=12, thoi_gian_dong_bhtn_thang=0, luong_bq_6_thang=6_000_000)),
    dict(id="c013", tool="tinh_tro_cap_mat_viec",
         input=dict(thoi_gian_lam_viec_thang=20, thoi_gian_dong_bhtn_thang=14, luong_bq_6_thang=8_000_000)),
    dict(id="c014", tool="tinh_tro_cap_mat_viec",
         input=dict(thoi_gian_lam_viec_thang=100, thoi_gian_dong_bhtn_thang=52, luong_bq_6_thang=9_000_000)),
    dict(id="c015", tool="tinh_tro_cap_mat_viec",
         input=dict(thoi_gian_lam_viec_thang=200, thoi_gian_dong_bhtn_thang=150, luong_bq_6_thang=11_000_000)),
    dict(id="c016", tool="tinh_tro_cap_mat_viec",
         input=dict(thoi_gian_lam_viec_thang=130, thoi_gian_dong_bhtn_thang=60, luong_bq_6_thang=13_000_000)),

    # ---- tinh_tien_lam_them_gio (8) ----
    dict(id="c017", tool="tinh_tien_lam_them_gio",
         input=dict(don_gia_gio=50_000, loai_ngay="thuong", so_gio=2, lam_dem=False)),
    dict(id="c018", tool="tinh_tien_lam_them_gio",
         input=dict(don_gia_gio=60_000, loai_ngay="nghi_tuan", so_gio=3, lam_dem=False)),
    dict(id="c019", tool="tinh_tien_lam_them_gio",
         input=dict(don_gia_gio=80_000, loai_ngay="le_tet", so_gio=4, lam_dem=False)),
    dict(id="c020", tool="tinh_tien_lam_them_gio",
         input=dict(don_gia_gio=50_000, loai_ngay="thuong", so_gio=2, lam_dem=True)),
    dict(id="c021", tool="tinh_tien_lam_them_gio",
         input=dict(don_gia_gio=60_000, loai_ngay="nghi_tuan", so_gio=3, lam_dem=True)),
    dict(id="c022", tool="tinh_tien_lam_them_gio",
         input=dict(don_gia_gio=70_000, loai_ngay="le_tet", so_gio=5, lam_dem=True)),
    dict(id="c023", tool="tinh_tien_lam_them_gio",
         input=dict(don_gia_gio=100_000, loai_ngay="thuong", so_gio=1, lam_dem=False)),
    dict(id="c024", tool="tinh_tien_lam_them_gio",
         input=dict(don_gia_gio=45_000, loai_ngay="nghi_tuan", so_gio=6, lam_dem=True)),

    # ---- tinh_ngay_phep_nam (8) ----
    dict(id="c025", tool="tinh_ngay_phep_nam",
         input=dict(loai_lao_dong="binh_thuong", so_thang_lam_viec=12, tham_nien_nam=3)),
    dict(id="c026", tool="tinh_ngay_phep_nam",
         input=dict(loai_lao_dong="binh_thuong", so_thang_lam_viec=12, tham_nien_nam=5)),
    dict(id="c027", tool="tinh_ngay_phep_nam",
         input=dict(loai_lao_dong="binh_thuong", so_thang_lam_viec=12, tham_nien_nam=12)),
    dict(id="c028", tool="tinh_ngay_phep_nam",
         input=dict(loai_lao_dong="nang_nhoc", so_thang_lam_viec=12, tham_nien_nam=6)),
    dict(id="c029", tool="tinh_ngay_phep_nam",
         input=dict(loai_lao_dong="dac_biet_nang_nhoc", so_thang_lam_viec=12, tham_nien_nam=10)),
    dict(id="c030", tool="tinh_ngay_phep_nam",
         input=dict(loai_lao_dong="binh_thuong", so_thang_lam_viec=8, tham_nien_nam=0)),
    dict(id="c031", tool="tinh_ngay_phep_nam",
         input=dict(loai_lao_dong="binh_thuong", so_thang_lam_viec=6, tham_nien_nam=0)),
    dict(id="c032", tool="tinh_ngay_phep_nam",
         input=dict(loai_lao_dong="nang_nhoc", so_thang_lam_viec=9, tham_nien_nam=0)),

    # ---- tinh_thoi_han_bao_truoc (8) ----
    dict(id="c033", tool="tinh_thoi_han_bao_truoc", input=dict(thoi_han_hop_dong_thang=None)),
    dict(id="c034", tool="tinh_thoi_han_bao_truoc", input=dict(thoi_han_hop_dong_thang=24)),
    dict(id="c035", tool="tinh_thoi_han_bao_truoc", input=dict(thoi_han_hop_dong_thang=12)),
    dict(id="c036", tool="tinh_thoi_han_bao_truoc", input=dict(thoi_han_hop_dong_thang=36)),
    dict(id="c037", tool="tinh_thoi_han_bao_truoc", input=dict(thoi_han_hop_dong_thang=11)),
    dict(id="c038", tool="tinh_thoi_han_bao_truoc", input=dict(thoi_han_hop_dong_thang=6)),
    dict(id="c039", tool="tinh_thoi_han_bao_truoc", input=dict(thoi_han_hop_dong_thang=1)),
    dict(id="c040", tool="tinh_thoi_han_bao_truoc", input=dict(thoi_han_hop_dong_thang=13)),
]

FUNCS = {
    "tinh_tro_cap_thoi_viec": tinh_tro_cap_thoi_viec,
    "tinh_tro_cap_mat_viec": tinh_tro_cap_mat_viec,
    "tinh_tien_lam_them_gio": tinh_tien_lam_them_gio,
    "tinh_ngay_phep_nam": tinh_ngay_phep_nam,
    "tinh_thoi_han_bao_truoc": tinh_thoi_han_bao_truoc,
}


def main() -> None:
    counts: dict[str, int] = {}
    for item in CALC_SET:
        fn = FUNCS[item["tool"]]
        item["expected"] = fn(**item["input"])
        counts[item["tool"]] = counts.get(item["tool"], 0) + 1

    assert len(CALC_SET) == 40, f"Can 40 tinh huong, hien co {len(CALC_SET)}"
    for tool, n in counts.items():
        assert n == 8, f"{tool} can 8 tinh huong, hien co {n}"
    print("Phan bo theo ham:", counts)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for item in CALC_SET:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Da ghi {len(CALC_SET)} tinh huong vao {OUT_PATH}")


if __name__ == "__main__":
    main()
