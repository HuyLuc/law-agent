"""Chay contract_rules.py tren 10 hop dong mau, do precision/recall cua
viec phat hien loi (PLAN.md Tuan 4 Buoi 3-4).

Chay: python scripts/eval_contract_review.py
"""

import json
from pathlib import Path

from src.tools.contract_rules import review_contract_file

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = ROOT / "data" / "eval" / "contracts"
OUT_PATH = ROOT / "eval" / "results" / "contract_review.json"


def main() -> None:
    ground_truth = json.loads((CONTRACTS_DIR / "ground_truth.json").read_text(encoding="utf-8"))

    tp = fp = fn = 0
    per_file = {}

    for filename, expected_rules in ground_truth.items():
        info, warnings = review_contract_file(CONTRACTS_DIR / filename)
        found_rules = {w["quy_tac"] for w in warnings}
        expected_set = set(expected_rules)

        file_tp = len(found_rules & expected_set)
        file_fp = len(found_rules - expected_set)
        file_fn = len(expected_set - found_rules)
        tp += file_tp
        fp += file_fp
        fn += file_fn

        per_file[filename] = {
            "expected": sorted(expected_set),
            "found": sorted(found_rules),
            "extracted_info": info.model_dump(),
        }
        print(f"{filename}: expected={sorted(expected_set)} found={sorted(found_rules)}")

    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    print(f"\nprecision={precision} recall={recall} (tp={tp} fp={fp} fn={fn})")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(
            {"precision": precision, "recall": recall, "tp": tp, "fp": fp, "fn": fn, "per_file": per_file},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Da luu ket qua vao {OUT_PATH}")


if __name__ == "__main__":
    main()
