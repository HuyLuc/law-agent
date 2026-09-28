"""V3: hybrid (V2) + reranker BAAI/bge-reranker-v2-m3.

Lay top-N tu search_hybrid, rerank roi giu top 5.

Do tren CPU (Intel i7-8565U), rerank 5 cap voi max_length=384: ban goc
(FlagEmbedding) ~27s/query -- khong kha thi cho ung dung thoi gian thuc.
Sau khi chuyen sang ONNX (Tuan 6 muc 2, xem scripts/export_onnx_reranker.py
+ eval/run_onnx_benchmark.py): ONNX fp32 ~13s/query (nhanh gap doi, Hit@5 va
MRR@5 giu nguyen y het) -- la backend mac dinh (RERANKER_BACKEND=onnx_fp32).
ONNX INT8 ~11s/query nhung MRR@5 giam nhe (0.914 -> 0.871), chi nen dung neu
uu tien toc do hon do chinh xac thu hang. Chi tiet so lieu:
eval/results/onnx_reranker.json.
"""

from functools import lru_cache
from pathlib import Path
from typing import Protocol

from src.config import settings
from src.retrieval.hybrid import search_hybrid

ROOT = Path(__file__).resolve().parents[2]
ONNX_FP32_DIR = ROOT / "data" / "models" / "bge-reranker-v2-m3-onnx"
ONNX_INT8_DIR = ROOT / "data" / "models" / "bge-reranker-v2-m3-onnx-int8"


class RerankerBackend(Protocol):
    def rerank(self, query: str, candidates: list[dict], top_k: int = 5, max_length: int = 384) -> list[dict]: ...


class Reranker:
    """Backend goc, dung truc tiep FlagEmbedding (khong can export truoc)."""

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


def _build_reranker() -> RerankerBackend:
    backend = settings.RERANKER_BACKEND
    if backend == "flagembedding":
        return Reranker()

    model_dir, file_name = {
        "onnx_fp32": (ONNX_FP32_DIR, None),
        "onnx_int8": (ONNX_INT8_DIR, "model_quantized.onnx"),
    }.get(backend, (None, None))
    if model_dir is None:
        raise ValueError(f"RERANKER_BACKEND khong hop le: {backend!r}")

    if not model_dir.exists():
        print(
            f"[reranker] RERANKER_BACKEND={backend!r} nhung chua thay {model_dir} -- "
            "chay `python -m scripts.export_onnx_reranker` truoc. Dung tam backend goc (FlagEmbedding)."
        )
        return Reranker()

    from src.retrieval.onnx_reranker import OnnxReranker

    return OnnxReranker(model_dir, file_name=file_name)


@lru_cache(maxsize=1)
def get_reranker() -> RerankerBackend:
    return _build_reranker()


def search_reranked(
    query: str, top_k: int = 5, prefetch_limit: int = 5, van_ban: str | None = None
) -> list[dict]:
    candidates = search_hybrid(
        query, top_k=prefetch_limit, prefetch_limit=prefetch_limit, van_ban=van_ban
    )
    return get_reranker().rerank(query, candidates, top_k=top_k)
