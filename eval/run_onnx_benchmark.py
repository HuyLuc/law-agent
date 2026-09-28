"""So sanh do tre CPU va Hit@5/MRR@5 giua reranker goc (FlagEmbedding) va
2 ban ONNX (fp32, int8) -- PLAN.md Tuan 6 muc 2.

Can chay `python -m scripts.export_onnx_reranker` truoc.

Do tre: benchmark rieng buoc rerank (khong tinh thoi gian truy van Qdrant/
dense-sparse encode) tren candidate co san, de so sanh cong bang.
Hit@5/MRR@5: chay het pipeline search_hybrid + rerank tren dev.jsonl, dung
lai eval/retrieval_metrics.py (cung dinh nghia voi ban chay tren Kaggle GPU).

Chay: python -m eval.run_onnx_benchmark
"""

import json
import time
from pathlib import Path

from eval.retrieval_metrics import evaluate
from src.retrieval.hybrid import search_hybrid
from src.retrieval.onnx_reranker import OnnxReranker
from src.retrieval.reranker import ONNX_FP32_DIR, ONNX_INT8_DIR, Reranker

ROOT = Path(__file__).resolve().parents[1]
DEV_PATH = ROOT / "data" / "eval" / "dev.jsonl"
PREFETCH_LIMIT = 5
MAX_LENGTH = 384
N_LATENCY_QUERIES = 15


def _load_dev() -> list[dict]:
    return [json.loads(line) for line in DEV_PATH.open(encoding="utf-8") if line.strip()]


def _bench_latency(name: str, reranker, queries_and_candidates: list[tuple[str, list[dict]]]) -> dict:
    print(f"Do do tre rerank: {name}...")
    reranker.rerank(*queries_and_candidates[0], top_k=5, max_length=MAX_LENGTH)  # warmup
    times = []
    for query, candidates in queries_and_candidates:
        t0 = time.time()
        reranker.rerank(query, candidates, top_k=5, max_length=MAX_LENGTH)
        times.append(time.time() - t0)
    times.sort()
    n = len(times)
    return {
        "avg_s": round(sum(times) / n, 3),
        "p50_s": round(times[n // 2], 3),
        "p95_s": round(times[min(n - 1, int(n * 0.95))], 3),
        "n": n,
    }


def _bench_quality(name: str, reranker) -> dict:
    print(f"Do Hit@5/MRR@5: {name}...")

    def search_fn(query: str, k: int) -> list[dict]:
        candidates = search_hybrid(query, top_k=PREFETCH_LIMIT, prefetch_limit=PREFETCH_LIMIT)
        return reranker.rerank(query, candidates, top_k=k, max_length=MAX_LENGTH)

    return evaluate(_load_dev(), search_fn, k_hit=5, k_mrr=10)


def main() -> None:
    dev = _load_dev()
    print("Chuan bi candidate co san (goi search_hybrid 1 lan, dung chung cho ca 3 backend)...")
    queries_and_candidates = [
        (item["question"], search_hybrid(item["question"], top_k=PREFETCH_LIMIT, prefetch_limit=PREFETCH_LIMIT))
        for item in dev[:N_LATENCY_QUERIES]
    ]

    backends = {
        "flagembedding_fp32": Reranker(),
        "onnx_fp32": OnnxReranker(ONNX_FP32_DIR),
        "onnx_int8": OnnxReranker(ONNX_INT8_DIR, file_name="model_quantized.onnx"),
    }

    results = {}
    for name, reranker in backends.items():
        results[name] = {
            "latency": _bench_latency(name, reranker, queries_and_candidates),
            "quality": _bench_quality(name, reranker),
        }
        print(name, results[name])

    out_path = ROOT / "eval" / "results" / "onnx_reranker.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Da luu ket qua vao {out_path}")


if __name__ == "__main__":
    main()
