"""Danh gia sinh cau tra loi cho V0-V4 (PLAN.md Tuan 4 Buoi 1-2).

Chi so: citation precision/recall, do dung (LLM giam khao 1-5), ty le tu
choi dung (nhom ngoai_pham_vi), do tre p50/p95. RAGAS faithfulness va do
chinh xac tinh toan duoc lam rieng (xem README khi hoan thanh).

Chay: python -m eval.run_generation_eval --dataset dev --versions v0,v1
"""

import argparse
import json
import time
from pathlib import Path

from pydantic import BaseModel, Field

from eval.citation_metrics import (
    average_non_none,
    citation_precision,
    citation_recall,
    extract_cited_dieu,
    extract_truth_dieu,
)
from eval.versions import answer_v0, answer_v1, answer_v2, answer_v3, answer_v4
from src.llm import build_llm_chain, structured_output_transform

ROOT = Path(__file__).resolve().parents[1]

VERSIONS = {
    "v0": (answer_v0, False),
    "v1": (answer_v1, False),
    "v2": (answer_v2, False),
    "v3": (answer_v3, False),
    "v4": (answer_v4, True),
}

REFUSAL_PATTERNS = [
    "không tìm thấy căn cứ",
    "ngoài phạm vi",
    "không liên quan",
    "không thuộc phạm vi",
    "không hỗ trợ",
    "không thể tư vấn",
]


class JudgeScore(BaseModel):
    diem: int = Field(ge=1, le=5, description="1=sai hoan toan, 5=dung hoan toan va day du")
    ly_do: str = Field(description="Giai thich ngan gon vi sao cho diem nay")


JUDGE_PROMPT = """Bạn là giám khảo chấm độ chính xác của câu trả lời về Luật Lao động Việt Nam.

Câu hỏi: {question}
Đáp án chuẩn: {ground_truth}
Câu trả lời cần chấm: {answer}

Chấm điểm 1-5:
5 = đúng hoàn toàn, đầy đủ nội dung chính so với đáp án chuẩn
4 = đúng phần lớn, thiếu chi tiết nhỏ không quan trọng
3 = đúng một phần, có ý đúng ý sai
2 = sai phần lớn nhưng còn liên quan đến câu hỏi
1 = sai hoàn toàn hoặc không liên quan
"""


def judge_answer(question: str, ground_truth: str, answer: str) -> int:
    llm = build_llm_chain(structured_output_transform(JudgeScore))
    result = llm.invoke(JUDGE_PROMPT.format(question=question, ground_truth=ground_truth, answer=answer))
    return result.diem


def is_refusal(answer: str) -> bool:
    lower = answer.lower()
    return any(p in lower for p in REFUSAL_PATTERNS)


def evaluate_version(name: str, dataset: list[dict]) -> dict:
    answer_fn, is_agent = VERSIONS[name]

    citation_p, citation_r, judge_scores, refusal_correct, latencies = [], [], [], [], []
    per_item = []

    for item in dataset:
        t0 = time.time()
        if is_agent:
            answer, _chunks = answer_fn(item["question"], thread_id=f"geneval_{name}_{item['id']}")
        else:
            answer, _chunks = answer_fn(item["question"])
        latency = time.time() - t0
        latencies.append(latency)

        interrupted = answer == "[AGENT_INTERRUPTED]"
        cited = extract_cited_dieu(answer) if not interrupted else set()
        truth = extract_truth_dieu(item["dieu_can_trich"])
        p = citation_precision(cited, truth)
        r = citation_recall(cited, truth)
        citation_p.append(p)
        citation_r.append(r)

        score = None if interrupted else judge_answer(item["question"], item["ground_truth"], answer)
        if score is not None:
            judge_scores.append(score)

        if item["loai"] == "ngoai_pham_vi":
            refusal_correct.append(is_refusal(answer) if not interrupted else False)

        per_item.append(
            {
                "id": item["id"],
                "loai": item["loai"],
                "answer": answer,
                "cited_dieu": sorted(cited),
                "truth_dieu": sorted(truth),
                "judge_score": score,
                "latency_s": round(latency, 2),
                "interrupted": interrupted,
            }
        )

    latencies_sorted = sorted(latencies)
    n = len(latencies_sorted)
    p50 = latencies_sorted[n // 2] if n else 0.0
    p95 = latencies_sorted[min(n - 1, int(n * 0.95))] if n else 0.0

    return {
        "citation_precision": average_non_none(citation_p),
        "citation_recall": average_non_none(citation_r),
        "avg_judge_score": sum(judge_scores) / len(judge_scores) if judge_scores else None,
        "refusal_accuracy": sum(refusal_correct) / len(refusal_correct) if refusal_correct else None,
        "latency_p50_s": round(p50, 2),
        "latency_p95_s": round(p95, 2),
        "n": len(dataset),
        "per_item": per_item,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["dev", "test"], default="dev")
    parser.add_argument("--versions", default="v0,v1,v2,v3,v4")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--ids", default=None, help="Danh sach id cach nhau boi dau phay (vd d001,d016), bo qua --limit"
    )
    parser.add_argument("--out-suffix", default="", help="Them hau to vao ten file ket qua (vd _sample)")
    args = parser.parse_args()

    data_path = ROOT / "data" / "eval" / f"{args.dataset}.jsonl"
    dataset = [json.loads(line) for line in data_path.open(encoding="utf-8")]
    if args.ids:
        wanted = set(args.ids.split(","))
        dataset = [item for item in dataset if item["id"] in wanted]
    elif args.limit:
        dataset = dataset[: args.limit]

    results = {}
    out_path = ROOT / "eval" / "results" / f"generation_{args.dataset}{args.out_suffix}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    for name in args.versions.split(","):
        print(f"=== {name} ===")
        result = evaluate_version(name, dataset)
        results[name] = result
        print({k: v for k, v in result.items() if k != "per_item"})
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Da luu ket qua vao {out_path}")


if __name__ == "__main__":
    main()
