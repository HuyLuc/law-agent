import json

from src.ingestion.parser import build_chunks

EXPECTED_DIEU_COUNT = {
    "45/2019/QH14": 220,
    "145/2020/NĐ-CP": 115,
    "293/2025/NĐ-CP": 5,
}


def _chunks():
    return build_chunks()


def test_article_counts_match_source_documents():
    chunks = _chunks()
    dieu_by_van_ban: dict[str, set[int]] = {}
    for c in chunks:
        dieu_by_van_ban.setdefault(c["so_hieu"], set()).add(c["dieu"])

    assert set(dieu_by_van_ban) == set(EXPECTED_DIEU_COUNT)
    for so_hieu, expected in EXPECTED_DIEU_COUNT.items():
        assert len(dieu_by_van_ban[so_hieu]) == expected, so_hieu


def test_no_empty_chunks():
    for c in _chunks():
        assert c["noi_dung"].strip(), c["id"]
        assert c["tieu_de_dieu"].strip(), c["id"]


def test_chunk_ids_are_unique():
    chunks = _chunks()
    ids = [c["id"] for c in chunks]
    assert len(ids) == len(set(ids))


def test_chunk_id_format():
    for c in _chunks():
        expected_khoan = c["khoan"] or 0
        assert c["id"].endswith(f"_D{c['dieu']}_K{expected_khoan}"), c["id"]


def test_decree_without_chapters_has_no_chuong():
    for c in _chunks():
        if c["so_hieu"] == "293/2025/NĐ-CP":
            assert c["chuong"] is None


def test_self_reference_excluded_from_dan_chieu():
    for c in _chunks():
        assert c["dieu"] not in c["dan_chieu"], c["id"]


def test_output_file_is_valid_jsonl_matching_build_chunks():
    from src.ingestion.parser import OUT_PATH

    with_file = [json.loads(line) for line in OUT_PATH.open(encoding="utf-8")]
    assert len(with_file) == len(_chunks())
