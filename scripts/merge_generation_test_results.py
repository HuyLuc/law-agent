"""Gop cac file generation_test_v*only.json thanh generation_test.json va in bang so sanh."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "eval" / "results"
OUT_FILE = RESULTS_DIR / "generation_test.json"
VERSIONS = ["v0", "v1", "v2", "v3", "v4"]


def merge_and_report() -> None:
    merged = {}
    for v in VERSIONS:
        file_path = RESULTS_DIR / f"generation_test_{v}only.json"
        if not file_path.exists():
            print(f"File {file_path.name} chua ton tai.")
            continue
        data = json.loads(file_path.read_text(encoding="utf-8"))
        if v in data:
            merged[v] = data[v]

    print(f"Da nap {len(merged)}/{len(VERSIONS)} phien ban:")
    for v, val in merged.items():
        n_items = len(val.get("per_item", []))
        metrics = val.get("metrics") or {
            k: val[k]
            for k in [
                "avg_judge_score",
                "citation_precision",
                "citation_recall",
                "refusal_accuracy",
                "latency_p50_s",
                "latency_p95_s",
            ]
            if k in val
        }
        print(f" - {v.upper()}: {n_items} cau | {metrics}")

    # Neu da du va tat ca deu co du 100 cau thi ghi file tong hop
    if all(v in merged and len(merged[v].get("per_item", [])) == 100 for v in VERSIONS):
        OUT_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nDa ghi toan bo ket qua vao: {OUT_FILE}")

        # In bang Markdown tong hop
        print("\n### Bang ket qua sinh cau tra loi tren bo TEST (n=100)")
        print("| Phien ban | Judge (1-5) | Citation P | Citation R | Tu choi dung | Do tre p50 | p95 |")
        print("|---|---|---|---|---|---|---|")
        labels = {
            "v0": "V0 — khong RAG",
            "v1": "V1 — dense RAG",
            "v2": "V2 — hybrid RAG",
            "v3": "V3 — hybrid + rerank",
            "v4": "V4 — agent day du",
        }
        for v in VERSIONS:
            m = merged[v]
            judge = f"{m['avg_judge_score']:.2f}" if m.get("avg_judge_score") else "-"
            cp = f"{m['citation_precision']:.2f}" if m.get("citation_precision") is not None else "-"
            cr = f"{m['citation_recall']:.2f}" if m.get("citation_recall") is not None else "-"
            refusal = f"{m['refusal_accuracy']:.2f}" if m.get("refusal_accuracy") is not None else "-"
            p50 = f"{m.get('latency_p50_s', 0):.0f}s"
            p95 = f"{m.get('latency_p95_s', 0):.0f}s"
            print(f"| {labels[v]} | {judge} | {cp} | {cr} | {refusal} | {p50} | {p95} |")


if __name__ == "__main__":
    merge_and_report()
