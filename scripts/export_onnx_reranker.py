"""Xuat BAAI/bge-reranker-v2-m3 sang ONNX roi luong tu hoa dong (INT8) de
chay nhanh hon tren CPU (PLAN.md Tuan 6 muc 2).

Chay: python -m scripts.export_onnx_reranker
Ket qua luu vao data/models/bge-reranker-v2-m3-onnx/ (fp32) va
data/models/bge-reranker-v2-m3-onnx-int8/ (quantized).
"""

from optimum.onnxruntime import ORTModelForSequenceClassification, ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from transformers import AutoTokenizer

from src.retrieval.reranker import ONNX_FP32_DIR as FP32_DIR
from src.retrieval.reranker import ONNX_INT8_DIR as INT8_DIR

MODEL_NAME = "BAAI/bge-reranker-v2-m3"


def main() -> None:
    FP32_DIR.mkdir(parents=True, exist_ok=True)
    INT8_DIR.mkdir(parents=True, exist_ok=True)

    print("Dang xuat sang ONNX (fp32)...")
    model = ORTModelForSequenceClassification.from_pretrained(MODEL_NAME, export=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model.save_pretrained(FP32_DIR)
    tokenizer.save_pretrained(FP32_DIR)

    print("Dang luong tu hoa dong sang INT8...")
    quantizer = ORTQuantizer.from_pretrained(model)
    qconfig = AutoQuantizationConfig.avx2(is_static=False, per_channel=False)
    quantizer.quantize(save_dir=INT8_DIR, quantization_config=qconfig)
    tokenizer.save_pretrained(INT8_DIR)

    print(f"Da luu fp32 -> {FP32_DIR}")
    print(f"Da luu int8 -> {INT8_DIR}")


if __name__ == "__main__":
    main()
