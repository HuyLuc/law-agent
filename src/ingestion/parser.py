"""Tach HTML van ban luat (data/raw/*.html, tai tu vbpl.vn) thanh chunks.jsonl.

vbpl.vn xuat HTML voi class ngu nghia san co: prov-chapter (Chuong),
prov-section (Muc), prov-article (Dieu), prov-clause (Khoan), prov-item
(Diem), prov-content (doan van xuoi khong danh so). Parser di qua cac the
<p> mang class do theo dung thu tu trong tai lieu va dung trang thai hien
tai (chuong/dieu/khoan) de gop noi dung.

Quy tac chia chunk (xem PLAN.md Tuan 1 Buoi 2-3):
- Moi Dieu la 1 chunk (khoan=None, id hau to _K0).
- Dieu dai hon ~800 token uoc luong thi tach theo Khoan, moi chunk con
  giu lai tieu de Dieu o dau.

Chay: python -m src.ingestion.parser
"""

import json
import re
import unicodedata
from pathlib import Path

import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
OUT_PATH = ROOT / "data" / "processed" / "chunks.jsonl"
SOURCES_PATH = RAW_DIR / "sources.yaml"

TARGET_CLASSES = {
    "prov-chapter",
    "prov-section",
    "prov-article",
    "prov-clause",
    "prov-item",
    "prov-content",
}

CHUONG_RE = re.compile(r"^Ch[uư]ơng\s+([IVXLCDM]+)\.?\s*(.*)$", re.IGNORECASE)
ARTICLE_RE = re.compile(r"^Điều\s+(\d+)\.\s*(.*)$")
CLAUSE_NUM_RE = re.compile(r"^(\d+)\.")
REFERENCE_RE = re.compile(r"Điều\s+(\d+)")

# Nguong token uoc luong (so tu, xap xi so token) de quyet dinh co tach
# Dieu theo Khoan hay khong.
MAX_TOKENS_PER_CHUNK = 800


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text).strip()


def estimate_tokens(text: str) -> int:
    return len(text.split())


def tag_class(tag) -> str | None:
    for c in tag.get("class", []):
        if c in TARGET_CLASSES:
            return c
    return None


def extract_references(text: str, self_dieu: int) -> list[int]:
    refs = {int(m) for m in REFERENCE_RE.findall(text)}
    refs.discard(self_dieu)
    return sorted(refs)


def parse_document(doc_id: str, meta: dict, html_path: Path) -> list[dict]:
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    tags = [t for t in soup.find_all("p") if tag_class(t)]

    chunks: list[dict] = []
    chuong_roman: str | None = None
    chapter_buffer: list[str] = []

    dieu_num: int | None = None
    dieu_title: str = ""
    dieu_intro: list[str] = []
    khoan_list: list[dict] = []  # [{"num": int|None, "lines": [str, ...]}]

    def flush_chapter_buffer() -> None:
        nonlocal chuong_roman, chapter_buffer
        if not chapter_buffer:
            return
        combined = normalize(" ".join(chapter_buffer))
        m = CHUONG_RE.match(combined)
        if m:
            chuong_roman = m.group(1)
        chapter_buffer = []

    def flush_dieu() -> None:
        nonlocal dieu_num, dieu_title, dieu_intro, khoan_list
        if dieu_num is None:
            return
        header = f"Điều {dieu_num}. {dieu_title}".strip()
        full_lines = [header] + dieu_intro + [
            line for k in khoan_list for line in k["lines"]
        ]
        full_text = "\n".join(full_lines)

        if not khoan_list or estimate_tokens(full_text) <= MAX_TOKENS_PER_CHUNK:
            chunks.append(_make_chunk(doc_id, meta, chuong_roman, dieu_num, dieu_title, None, full_text))
        else:
            for k in khoan_list:
                sub_lines = [header] + dieu_intro + k["lines"]
                sub_text = "\n".join(sub_lines)
                chunks.append(
                    _make_chunk(doc_id, meta, chuong_roman, dieu_num, dieu_title, k["num"], sub_text)
                )

        dieu_num = None
        dieu_title = ""
        dieu_intro = []
        khoan_list = []

    for tag in tags:
        cls = tag_class(tag)
        text = normalize(tag.get_text(" ", strip=True))
        if not text:
            continue

        if cls == "prov-chapter":
            flush_dieu()
            chapter_buffer.append(text)
            continue
        else:
            flush_chapter_buffer()

        if cls == "prov-section":
            continue  # Muc: khong co truong rieng trong schema chunk hien tai

        if cls == "prov-article":
            flush_dieu()
            m = ARTICLE_RE.match(text)
            if not m:
                raise ValueError(f"{doc_id}: khong parse duoc tieu de Dieu: {text!r}")
            dieu_num = int(m.group(1))
            dieu_title = m.group(2)
            continue

        if cls == "prov-clause":
            m = CLAUSE_NUM_RE.match(text)
            khoan_num = int(m.group(1)) if m else None
            khoan_list.append({"num": khoan_num, "lines": [text]})
            continue

        if cls == "prov-item":
            if khoan_list:
                khoan_list[-1]["lines"].append(text)
            else:
                dieu_intro.append(text)
            continue

        if cls == "prov-content":
            if khoan_list:
                khoan_list[-1]["lines"].append(text)
            else:
                dieu_intro.append(text)
            continue

    flush_dieu()
    return chunks


def _make_chunk(
    doc_id: str,
    meta: dict,
    chuong: str | None,
    dieu: int,
    tieu_de_dieu: str,
    khoan: int | None,
    noi_dung: str,
) -> dict:
    return {
        "id": f"{doc_id}_D{dieu}_K{khoan or 0}",
        "van_ban": meta["ten"],
        "so_hieu": meta["so_hieu"],
        "chuong": chuong,
        "dieu": dieu,
        "khoan": khoan,
        "tieu_de_dieu": tieu_de_dieu,
        "noi_dung": noi_dung,
        "dan_chieu": extract_references(noi_dung, dieu),
        "hieu_luc_tu": str(meta["hieu_luc_tu"]),
    }


def build_chunks() -> list[dict]:
    sources = yaml.safe_load(SOURCES_PATH.read_text(encoding="utf-8"))
    all_chunks: list[dict] = []
    for meta in sources:
        html_path = ROOT / "data" / meta["file"]
        all_chunks.extend(parse_document(meta["id"], meta, html_path))
    return all_chunks


def main() -> None:
    chunks = build_chunks()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"Da ghi {len(chunks)} chunk vao {OUT_PATH}")


if __name__ == "__main__":
    main()
