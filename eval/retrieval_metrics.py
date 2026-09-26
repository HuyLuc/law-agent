"""Hit@k va MRR@k cho phan tim kiem (xem PLAN.md muc 7.3).

Cau hoi thuoc nhom `ngoai_pham_vi` khong co `dieu_can_trich` nen duoc bo
qua khoi phep tinh (khong co gi de tim).
"""

from collections.abc import Callable, Iterable


def hit_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> bool:
    return any(rid in relevant_ids for rid in retrieved_ids[:k])


def mrr_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    for rank, rid in enumerate(retrieved_ids[:k], start=1):
        if rid in relevant_ids:
            return 1.0 / rank
    return 0.0


def evaluate(
    dataset: Iterable[dict],
    search_fn: Callable[[str, int], list[dict]],
    k_hit: int = 5,
    k_mrr: int = 10,
) -> dict:
    hits: list[bool] = []
    mrrs: list[float] = []
    top_k = max(k_hit, k_mrr)

    for item in dataset:
        relevant = set(item.get("dieu_can_trich") or [])
        if not relevant:
            continue
        results = search_fn(item["question"], top_k)
        retrieved_ids = [r["id"] for r in results]
        hits.append(hit_at_k(retrieved_ids, relevant, k_hit))
        mrrs.append(mrr_at_k(retrieved_ids, relevant, k_mrr))

    return {
        "hit_at_k": sum(hits) / len(hits) if hits else 0.0,
        "mrr_at_k": sum(mrrs) / len(mrrs) if mrrs else 0.0,
        "n": len(hits),
    }
