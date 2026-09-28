"""Citation precision/recall: so sanh Dieu duoc TRICH DAN trong cau tra loi
(khong phai Dieu duoc tra ve) voi dieu_can_trich (PLAN.md muc 7.3)."""

import re

_DIEU_RE = re.compile(r"Điều\s+(\d+)")
_CHUNK_ID_DIEU_RE = re.compile(r"_D(\d+)_K")


def extract_cited_dieu(answer_text: str) -> set[int]:
    return {int(m) for m in _DIEU_RE.findall(answer_text)}


def extract_truth_dieu(dieu_can_trich: list[str]) -> set[int]:
    result: set[int] = set()
    for chunk_id in dieu_can_trich:
        m = _CHUNK_ID_DIEU_RE.search(chunk_id)
        if m:
            result.add(int(m.group(1)))
    return result


def citation_precision(cited: set[int], truth: set[int]) -> float | None:
    """None neu khong trich Dieu nao ca (khong ap dung duoc precision)."""
    if not cited:
        return None
    return len(cited & truth) / len(cited)


def citation_recall(cited: set[int], truth: set[int]) -> float | None:
    """None neu cau hoi khong co dieu_can_trich (vd nhom ngoai_pham_vi)."""
    if not truth:
        return None
    return len(cited & truth) / len(truth)


def average_non_none(values: list[float | None]) -> float | None:
    filtered = [v for v in values if v is not None]
    return sum(filtered) / len(filtered) if filtered else None
