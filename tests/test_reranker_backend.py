"""Test logic chon backend reranker (khong tai model that -- xem PLAN.md Tuan 6 muc 2)."""

import pytest

from src.retrieval import reranker as rr


def test_flagembedding_backend_tra_ve_reranker_goc(monkeypatch):
    monkeypatch.setattr(rr.settings, "RERANKER_BACKEND", "flagembedding")
    assert isinstance(rr._build_reranker(), rr.Reranker)


def test_onnx_backend_fallback_ve_goc_khi_chua_export(monkeypatch, tmp_path):
    monkeypatch.setattr(rr.settings, "RERANKER_BACKEND", "onnx_fp32")
    monkeypatch.setattr(rr, "ONNX_FP32_DIR", tmp_path / "khong_ton_tai")
    assert isinstance(rr._build_reranker(), rr.Reranker)


def test_backend_khong_hop_le_bao_loi(monkeypatch):
    monkeypatch.setattr(rr.settings, "RERANKER_BACKEND", "vo_ly")
    with pytest.raises(ValueError, match="vo_ly"):
        rr._build_reranker()


def test_reranker_fast_path_0_hoac_1_candidate_khong_goi_model(monkeypatch):
    reranker = rr.Reranker()

    def _boom(_self):
        raise AssertionError("Khong duoc khoi tao hay goi model khi len(candidates) <= 1")

    monkeypatch.setattr(rr.Reranker, "model", property(_boom))

    assert reranker.rerank("thử việc", [], top_k=5) == []

    single = [{"id": "BLLD2019_D25_K0", "noi_dung": "Thời gian thử việc..."}]
    assert reranker.rerank("thử việc", single, top_k=5) == single
    assert reranker._model is None


def test_search_reranked_fast_path_1_candidate_khong_goi_get_reranker(monkeypatch):
    single = [{"id": "BLLD2019_D25_K0", "noi_dung": "Thời gian thử việc..."}]
    monkeypatch.setattr(rr, "search_hybrid", lambda *_args, **_kwargs: single)

    def _boom():
        raise AssertionError("Khong duoc goi get_reranker khi len(candidates) <= 1")

    monkeypatch.setattr(rr, "get_reranker", _boom)

    assert rr.search_reranked("thử việc", top_k=5) == single


def test_onnx_reranker_fast_path_0_hoac_1_candidate_khong_load_model(monkeypatch, tmp_path):
    from src.retrieval.onnx_reranker import OnnxReranker

    onnx_rr = OnnxReranker(tmp_path / "dummy")

    def _boom(_self):
        raise AssertionError("Khong duoc goi _ensure_loaded khi len(candidates) <= 1")

    monkeypatch.setattr(OnnxReranker, "_ensure_loaded", _boom)

    assert onnx_rr.rerank("thử việc", [], top_k=5) == []
    single = [{"id": "BLLD2019_D25_K0", "noi_dung": "Thời gian thử việc..."}]
    assert onnx_rr.rerank("thử việc", single, top_k=5) == single

