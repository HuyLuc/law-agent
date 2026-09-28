"""Reranker ONNX (fp32 hoac INT8) cho BAAI/bge-reranker-v2-m3, cung giao dien
`.rerank(query, candidates, top_k, max_length)` nhu Reranker o reranker.py
(xem PLAN.md Tuan 6 muc 2 -- doi chieu do tre CPU truoc/sau voi
scripts/export_onnx_reranker.py + eval/run_onnx_benchmark.py).

Can chay `python -m scripts.export_onnx_reranker` truoc de tao thu muc
model_dir (data/models/bge-reranker-v2-m3-onnx[-int8]/).
"""

from pathlib import Path

import numpy as np


class OnnxReranker:
    def __init__(self, model_dir: Path | str, file_name: str | None = None) -> None:
        self._model_dir = str(model_dir)
        self._file_name = file_name
        self._model = None
        self._tokenizer = None

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        from optimum.onnxruntime import ORTModelForSequenceClassification
        from transformers import AutoTokenizer

        kwargs = {"file_name": self._file_name} if self._file_name else {}
        self._model = ORTModelForSequenceClassification.from_pretrained(self._model_dir, **kwargs)
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_dir)

    def rerank(self, query: str, candidates: list[dict], top_k: int = 5, max_length: int = 384) -> list[dict]:
        if not candidates:
            return []
        self._ensure_loaded()
        texts = [c["noi_dung"] for c in candidates]
        inputs = self._tokenizer(
            [query] * len(texts),
            texts,
            truncation=True,
            max_length=max_length,
            padding=True,
            return_tensors="pt",
        )
        logits = self._model(**inputs).logits.squeeze(-1).detach().numpy()
        scores = 1.0 / (1.0 + np.exp(-logits))  # sigmoid, giong normalize=True cua FlagReranker
        ranked = sorted(zip(candidates, scores.tolist(), strict=True), key=lambda x: x[1], reverse=True)
        return [c for c, _score in ranked[:top_k]]
