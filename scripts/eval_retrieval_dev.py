"""Chay Hit@5 / MRR@10 cho V1/V2/V3 tren tap dev.jsonl (Tuan 2, Buoi 3).

Chay: python scripts/eval_retrieval_dev.py
"""

import json
import time
from pathlib import Path

from eval.retrieval_metrics import evaluate
from src.retrieval.hybrid import search_dense, search_hybrid
from src.retrieval.reranker import search_reranked

ROOT = Path(__file__).resolve().parents[1]
DEV_PATH = ROOT / "data" / "eval" / "dev.jsonl"


def main() -> None:
    dataset = [json.loads(line) for line in DEV_PATH.open(encoding="utf-8")]

    versions = {
        "V1_dense": lambda q, k: search_dense(q, top_k=k),
        "V2_hybrid": lambda q, k: search_hybrid(q, top_k=k, prefetch_limit=20),
        "V3_hybrid_rerank_top10": lambda q, k: search_reranked(q, top_k=k, prefetch_limit=10),
        "V3_hybrid_rerank_top20": lambda q, k: search_reranked(q, top_k=k, prefetch_limit=20),
    }

    results = {}
    for name, fn in versions.items():
        t0 = time.time()
        metrics = evaluate(dataset, fn, k_hit=5, k_mrr=10)
        metrics["eval_time_s"] = round(time.time() - t0, 1)
        results[name] = metrics
        print(f"{name}: {metrics}")

    out_path = ROOT / "eval" / "results" / "retrieval_dev.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Da luu ket qua vao {out_path}")


if __name__ == "__main__":
    main()
