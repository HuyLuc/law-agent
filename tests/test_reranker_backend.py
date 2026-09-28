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
