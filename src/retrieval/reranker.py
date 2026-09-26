"""V3: hybrid (V2) + reranker BAAI/bge-reranker-v2-m3.

Lay top-N tu search_hybrid, rerank roi giu top 5.

Do tren CPU (Intel i7-8565U): rerank 20 cap khong gioi han do dai ~188s/query
(khong kha thi cho app thoi gian thuc). Sau khi gioi han max_length=384 va
giam con 5 cap prefetch (theo dung mitigation trong PLAN.md muc 8 "Reranker
chay cham tren CPU"), con ~30s/query (do thuc te tren eval/results/retrieval_dev.json)
-- van rat cham cho ung dung thoi gian thuc, se can ban ONNX INT8 o Tuan 6
neu muon dua vao production that.
"""

from functools import lru_cache

from src.retrieval.hybrid import search_hybrid


class Reranker:
    def __init__(self) -> None:
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from FlagEmbedding import FlagReranker

            self._model = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=False)
        return self._model

    def rerank(
        self, query: str, candidates: list[dict], top_k: int = 5, max_length: int = 384
    ) -> list[dict]:
        if not candidates:
            return []
        pairs = [[query, c["noi_dung"]] for c in candidates]
        scores = self.model.compute_score(pairs, normalize=True, max_length=max_length)
        if isinstance(scores, float):
            scores = [scores]
        ranked = sorted(zip(candidates, scores, strict=True), key=lambda x: x[1], reverse=True)
        return [c for c, _score in ranked[:top_k]]


@lru_cache(maxsize=1)
def get_reranker() -> Reranker:
    return Reranker()


def search_reranked(query: str, top_k: int = 5, prefetch_limit: int = 5) -> list[dict]:
    candidates = search_hybrid(query, top_k=prefetch_limit, prefetch_limit=prefetch_limit)
    return get_reranker().rerank(query, candidates, top_k=top_k)
