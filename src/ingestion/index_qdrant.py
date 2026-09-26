"""Dua chunks.jsonl + embeddings.parquet (tai tu Kaggle) vao Qdrant.

Collection co 2 loai vector: "dense" (1024 chieu, cosine) va "sparse".
Point id la UUID5 sinh tu id chuoi cua chunk (on dinh qua cac lan chay lai);
id chuoi goc va toan bo metadata cua chunk duoc luu trong payload.

Chay: python -m src.ingestion.index_qdrant
"""

import json
import uuid
from pathlib import Path

import pandas as pd
from qdrant_client import QdrantClient, models

from src.config import settings

ROOT = Path(__file__).resolve().parents[2]
CHUNKS_PATH = ROOT / "data" / "processed" / "chunks.jsonl"
EMBEDDINGS_PATH = ROOT / "data" / "embeddings" / "embeddings.parquet"

NAMESPACE = uuid.UUID("6f7b1a2e-1c8f-4a1a-9b2e-2f6a1e8b7c11")


def chunk_point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(NAMESPACE, chunk_id))


def load_chunks() -> dict[str, dict]:
    chunks = {}
    with CHUNKS_PATH.open(encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            chunks[c["id"]] = c
    return chunks


def build_collection(client: QdrantClient, collection_name: str) -> None:
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            "dense": models.VectorParams(size=1024, distance=models.Distance.COSINE),
        },
        sparse_vectors_config={
            "sparse": models.SparseVectorParams(),
        },
    )


def index(client: QdrantClient | None = None, collection_name: str | None = None) -> int:
    client = client or QdrantClient(url=settings.QDRANT_URL)
    collection_name = collection_name or settings.QDRANT_COLLECTION

    chunks = load_chunks()
    df = pd.read_parquet(EMBEDDINGS_PATH)

    build_collection(client, collection_name)

    points = []
    for _, row in df.iterrows():
        chunk = chunks.get(row["id"])
        if chunk is None:
            raise ValueError(f"Khong tim thay chunk cho id {row['id']} trong chunks.jsonl")
        points.append(
            models.PointStruct(
                id=chunk_point_id(row["id"]),
                vector={
                    "dense": list(row["dense"]),
                    "sparse": models.SparseVector(
                        indices=list(row["sparse_indices"]),
                        values=list(row["sparse_values"]),
                    ),
                },
                payload=chunk,
            )
        )

    client.upsert(collection_name=collection_name, points=points)
    return len(points)


def main() -> None:
    n = index()
    print(f"Da index {n} chunk vao collection '{settings.QDRANT_COLLECTION}'")


if __name__ == "__main__":
    main()
