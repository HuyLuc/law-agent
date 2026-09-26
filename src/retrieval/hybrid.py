"""Cac phien ban tim kiem V1 (dense) va V2 (hybrid dense+sparse, RRF).

V3 (hybrid + rerank) duoc lap trong reranker.py, goi lai search_hybrid o day
voi prefetch_limit lon hon roi rerank xuong con top_k.
"""

from functools import lru_cache

from qdrant_client import QdrantClient, models

from src.config import settings
from src.retrieval.embedder import get_embedder


@lru_cache(maxsize=1)
def get_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL)


def search_dense(query: str, top_k: int = 5) -> list[dict]:
    """V1: chi dung vector day (dense), khong dung tu khoa."""
    dense, _sparse = get_embedder().encode_query(query)
    res = get_client().query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=dense,
        using="dense",
        limit=top_k,
    )
    return [p.payload for p in res.points]


def search_hybrid(query: str, top_k: int = 5, prefetch_limit: int = 20) -> list[dict]:
    """V2: hybrid dense + sparse (tu khoa), gop bang RRF."""
    dense, sparse = get_embedder().encode_query(query)
    sparse_vector = models.SparseVector(
        indices=list(sparse.keys()),
        values=list(sparse.values()),
    )
    res = get_client().query_points(
        collection_name=settings.QDRANT_COLLECTION,
        prefetch=[
            models.Prefetch(query=dense, using="dense", limit=prefetch_limit),
            models.Prefetch(query=sparse_vector, using="sparse", limit=prefetch_limit),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=top_k,
    )
    return [p.payload for p in res.points]
