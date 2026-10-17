"""Phan tich loi (Error Analysis) tren ket qua danh gia sinh cau tra loi (PLAN.md Tuan 4)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "eval" / "results"


def analyze_errors(version: str = "v4", dataset: str = "test") -> None:
    file_path = RESULTS_DIR / f"generation_{dataset}_{version}only.json"
    if not file_path.exists():
        file_path = RESULTS_DIR / f"generation_{dataset}.json"
    if not file_path.exists():
        print(f"Khong tim thay file ket qua cho {version} tren {dataset}")
        return

    data = json.loads(file_path.read_text(encoding="utf-8"))
    ver_data = data.get(version, {})
    per_item = ver_data.get("per_item", [])
    if not per_item:
        print("Khong co du lieu per_item.")
        return

    print(f"=== PHAN TICH LOI CHO {version.upper()} TREN TAP {dataset.upper()} ({len(per_item)} cau) ===")

    # 1. Cac cau bi diem giam khao thap (< 4)
    low_judge = [it for it in per_item if it.get("judge_score") is not None and it["judge_score"] < 4]
    print(f"\n1. So cau co diem giam khao < 4: {len(low_judge)}")
    for it in low_judge[:5]:
        print(f" - [{it['id']} - {it['loai']}] Diem: {it['judge_score']}")
        print(f"   Trich dan: {it.get('cited_dieu')} | Chuan: {it.get('truth_dieu')}")
        print(f"   Cau tra loi: {it['answer'][:150]}...\n")

    # 2. Cac cau co citation recall thap (< 0.7)
    low_cr = [it for it in per_item if it.get("citation_r") is not None and it["citation_r"] < 0.7]
    print(f"\n2. So cau co Citation Recall < 0.7: {len(low_cr)}")
    for it in low_cr[:5]:
        print(f" - [{it['id']} - {it['loai']}] Recall: {it.get('citation_r')}")
        print(f"   Trich dan: {it.get('cited_dieu')} | Chuan: {it.get('truth_dieu')}\n")

    # 3. Cac cau ngoai pham vi bi tu choi sai
    wrong_refusal = [it for it in per_item if it.get("refusal_correct") is False]
    print(f"\n3. So cau ngoai pham vi bi tu choi sai (khong tu choi): {len(wrong_refusal)}")
    for it in wrong_refusal:
        print(f" - [{it['id']}] {it['answer'][:150]}...\n")


if __name__ == "__main__":
    analyze_errors("v4", "test")
