"""Tao embedding bge-m3 (dense + sparse) cho cau hoi, chay tren CPU.

Dung cung mo hinh BAAI/bge-m3 nhu luc tao embedding hang loat tren Kaggle
(kaggle/01_embed_chunks.ipynb) de dense/sparse vector tuong thich nhau.
"""

from functools import lru_cache


class Embedder:
    def __init__(self) -> None:
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from FlagEmbedding import BGEM3FlagModel

            self._model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=False)
        return self._model

    def encode_query(self, text: str) -> tuple[list[float], dict[int, float]]:
        output = self.model.encode(
            [text],
            max_length=1024,
            return_dense=True,
            return_sparse=True,
        )
        dense = output["dense_vecs"][0].tolist()
        sparse_raw = output["lexical_weights"][0]
        sparse = {int(token_id): float(weight) for token_id, weight in sparse_raw.items()}
        return dense, sparse


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    return Embedder()
