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


def _aggregate(per_item: list[dict], n_total: int) -> dict:
    citation_p = [it["citation_p"] for it in per_item if it.get("citation_p") is not None]
    citation_r = [it["citation_r"] for it in per_item if it.get("citation_r") is not None]
    judge_scores = [it["judge_score"] for it in per_item if it.get("judge_score") is not None]
    refusal_correct = [it["refusal_correct"] for it in per_item if it.get("refusal_correct") is not None]
    latencies_sorted = sorted(it["latency_s"] for it in per_item)
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
        "n": n_total,
        "per_item": per_item,
    }


def evaluate_version(
    name: str, dataset: list[dict], out_path: Path, results: dict, done_ids: set[str], per_item: list[dict]
) -> None:
    """Chay 1 phien ban, GHI FILE SAU MOI CAU HOI (khong doi het ca phien ban
    moi ghi) -- can thiet vi tien trinh co the bi kill (gioi han chay nen
    2 gio) truoc khi chay het 100 cau cua bo test; checkpoint theo cau giup
    chay lai (resume) khong mat tien do da co, chi bo qua id da xong."""
    answer_fn, is_agent = VERSIONS[name]

    for item in dataset:
        if item["id"] in done_ids:
            continue
        t0 = time.time()
        if is_agent:
            answer, _chunks = answer_fn(item["question"], thread_id=f"geneval_{name}_{item['id']}")
        else:
            answer, _chunks = answer_fn(item["question"])
        latency = time.time() - t0

        interrupted = answer == "[AGENT_INTERRUPTED]"
        cited = extract_cited_dieu(answer) if not interrupted else set()
        truth = extract_truth_dieu(item["dieu_can_trich"])
        p = citation_precision(cited, truth)
        r = citation_recall(cited, truth)

        score = None if interrupted else judge_answer(item["question"], item["ground_truth"], answer)

        refusal_correct = None
        if item["loai"] == "ngoai_pham_vi":
            refusal_correct = is_refusal(answer) if not interrupted else False

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
                "citation_p": p,
                "citation_r": r,
                "refusal_correct": refusal_correct,
            }
        )
        done_ids.add(item["id"])

        results[name] = _aggregate(per_item, len(dataset))
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{name}] {len(done_ids)}/{len(dataset)} xong (vua xong: {item['id']})")


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

    out_path = ROOT / "eval" / "results" / f"generation_{args.dataset}{args.out_suffix}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results = {}
    if out_path.exists():
        try:
            results = json.loads(out_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            results = {}

    for name in args.versions.split(","):
        print(f"=== {name} ===")
        existing = results.get(name, {})
        per_item = existing.get("per_item", [])
        done_ids = {it["id"] for it in per_item}
        if len(done_ids) >= len(dataset):
            print(f"[{name}] da xong tu truoc ({len(done_ids)}/{len(dataset)}), bo qua")
            continue
        if done_ids:
            print(f"[{name}] resume: {len(done_ids)}/{len(dataset)} da xong tu truoc")
        evaluate_version(name, dataset, out_path, results, done_ids, per_item)
        print({k: v for k, v in results[name].items() if k != "per_item"})

    print(f"Da luu ket qua vao {out_path}")


if __name__ == "__main__":
    main()
