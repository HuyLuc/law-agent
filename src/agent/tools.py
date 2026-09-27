"""Boc cac ham thuan Python (legal_lookup, calculators) thanh LangChain tool.

Dung response_format="content_and_artifact": "content" la text cho LLM doc,
"artifact" la du lieu tho (chunk hoac ket qua tinh toan) de node agent_loop
dung cap nhat state["evidence"] ma khong lam nhieu ngu canh cua LLM.
"""

from langchain_core.tools import tool
from langgraph.types import interrupt

from src.tools import calculators
from src.tools.legal_lookup import follow_references, get_article, search_law


def _format_chunks(chunks: list[dict]) -> str:
    if not chunks:
        return "Không tìm thấy kết quả phù hợp."
    return "\n\n".join(
        f"[{c['id']}] Điều {c['dieu']}"
        + (f" Khoản {c['khoan']}" if c.get("khoan") else "")
        + f" - {c['van_ban']}\n{c['noi_dung']}"
        for c in chunks
    )


@tool(response_format="content_and_artifact")
def search_law_tool(query: str, van_ban: str | None = None) -> tuple[str, list[dict]]:
    """Tim kiem dieu luat theo ngu nghia khi chua biet chinh xac so Dieu can tra.

    Dung V3 (hybrid dense+sparse + rerank), tra ve toi da 5 doan luat lien quan nhat.

    Args:
        query: Cau hoi hoac tu khoa can tim (tieng Viet).
        van_ban: Neu chi muon tim trong 1 van ban cu the, truyen ten van ban
            (vi du "Bộ luật Lao động 2019"). De trong neu muon tim tren tat ca.
    """
    chunks = search_law(query, van_ban)
    return _format_chunks(chunks), chunks


@tool(response_format="content_and_artifact")
def get_article_tool(van_ban: str, dieu: int, khoan: int | None = None) -> tuple[str, list[dict]]:
    """Tra chinh xac noi dung 1 Dieu (hoac 1 Khoan) theo so hieu, KHONG tim ngu nghia.

    Dung khi da biet chinh xac so Dieu can tra (vi du da thay "Điều 46" duoc
    dan chieu trong ket qua truoc do).

    Args:
        van_ban: Ten van ban (vi du "Bộ luật Lao động 2019") hoac so hieu
            (vi du "45/2019/QH14").
        dieu: So Dieu can tra.
        khoan: So Khoan can tra; de trong de lay toan bo Dieu.
    """
    chunks = get_article(van_ban, dieu, khoan)
    return _format_chunks(chunks), chunks


@tool(response_format="content_and_artifact")
def follow_references_tool(chunk_id: str) -> tuple[str, list[dict]]:
    """Tra tiep cac Dieu duoc dan chieu boi 1 doan luat da tra truoc do.

    Args:
        chunk_id: Ma "id" cua doan luat goc (vi du "BLLD2019_D45_K0"), lay tu
            ket qua cua search_law_tool hoac get_article_tool.
    """
    chunks = follow_references(chunk_id)
    return _format_chunks(chunks), chunks


def _format_calc_result(result: dict) -> str:
    can_cu = ", ".join(result["can_cu"])
    return f"Kết quả: {result['ket_qua']}\nCách tính: {result['cach_tinh']}\nCăn cứ: {can_cu}"


@tool(response_format="content_and_artifact")
def tinh_tro_cap_thoi_viec_tool(
    thoi_gian_lam_viec_thang: int, thoi_gian_dong_bhtn_thang: int, luong_bq_6_thang: float
) -> tuple[str, dict]:
    """Tinh tro cap thoi viec (Dieu 46 BLLD 2019 + Dieu 8 ND145/2020).

    Args:
        thoi_gian_lam_viec_thang: Tong thoi gian lam viec thuc te (thang).
        thoi_gian_dong_bhtn_thang: Thoi gian da tham gia bao hiem that nghiep (thang).
        luong_bq_6_thang: Luong binh quan 6 thang lien ke truoc khi nghi viec (dong).
    """
    result = calculators.tinh_tro_cap_thoi_viec(
        thoi_gian_lam_viec_thang, thoi_gian_dong_bhtn_thang, luong_bq_6_thang
    )
    return _format_calc_result(result), result


@tool(response_format="content_and_artifact")
def tinh_tro_cap_mat_viec_tool(
    thoi_gian_lam_viec_thang: int, thoi_gian_dong_bhtn_thang: int, luong_bq_6_thang: float
) -> tuple[str, dict]:
    """Tinh tro cap mat viec lam (Dieu 47 BLLD 2019 + Dieu 8 ND145/2020).

    Args:
        thoi_gian_lam_viec_thang: Tong thoi gian lam viec thuc te (thang).
        thoi_gian_dong_bhtn_thang: Thoi gian da tham gia bao hiem that nghiep (thang).
        luong_bq_6_thang: Luong binh quan 6 thang lien ke truoc khi mat viec (dong).
    """
    result = calculators.tinh_tro_cap_mat_viec(
        thoi_gian_lam_viec_thang, thoi_gian_dong_bhtn_thang, luong_bq_6_thang
    )
    return _format_calc_result(result), result


@tool(response_format="content_and_artifact")
def tinh_tien_lam_them_gio_tool(
    don_gia_gio: float, loai_ngay: str, so_gio: float, lam_dem: bool
) -> tuple[str, dict]:
    """Tinh tien luong lam them gio (Dieu 98 BLLD 2019).

    Args:
        don_gia_gio: Don gia tien luong theo gio cua ngay lam viec binh thuong (dong).
        loai_ngay: "thuong" (ngay thuong), "nghi_tuan" (ngay nghi hang tuan), hoac
            "le_tet" (ngay nghi le, tet, ngay nghi co huong luong).
        so_gio: So gio lam them.
        lam_dem: True neu lam them gio do vao ban dem.
    """
    result = calculators.tinh_tien_lam_them_gio(don_gia_gio, loai_ngay, so_gio, lam_dem)
    return _format_calc_result(result), result


@tool(response_format="content_and_artifact")
def tinh_ngay_phep_nam_tool(
    loai_lao_dong: str, so_thang_lam_viec: int, tham_nien_nam: int
) -> tuple[str, dict]:
    """Tinh so ngay nghi phep nam (Dieu 113-114 BLLD 2019).

    Args:
        loai_lao_dong: "binh_thuong" (12 ngay co ban), "nang_nhoc" (14 ngay), hoac
            "dac_biet_nang_nhoc" (16 ngay).
        so_thang_lam_viec: So thang da lam trong nam hien tai (1-12).
        tham_nien_nam: Tong so nam da lam cho nguoi su dung lao dong nay (de tinh
            ngay phep cong them theo tham nien, chi ap dung khi so_thang_lam_viec=12).
    """
    result = calculators.tinh_ngay_phep_nam(loai_lao_dong, so_thang_lam_viec, tham_nien_nam)
    return _format_calc_result(result), result


@tool(response_format="content_and_artifact")
def tinh_thoi_han_bao_truoc_tool(thoi_han_hop_dong_thang: int | None) -> tuple[str, dict]:
    """Tinh thoi han bao truoc khi don phuong cham dut hop dong lao dong (Dieu 35-36 BLLD 2019).

    Args:
        thoi_han_hop_dong_thang: So thang thoi han hop dong lao dong; de None neu
            hop dong khong xac dinh thoi han.
    """
    result = calculators.tinh_thoi_han_bao_truoc(thoi_han_hop_dong_thang)
    return _format_calc_result(result), result


@tool
def ask_user(question: str) -> str:
    """Hoi lai nguoi dung khi thieu thong tin quyet dinh de tra loi chinh xac
    (vi du: loai hop dong, tham nien, muc luong, vung luong toi thieu...).
    KHONG tu gia dinh cac thong tin nay.

    Args:
        question: Cau hoi ro rang, cu the de hoi nguoi dung.
    """
    return interrupt({"question": question})


ALL_TOOLS = [
    search_law_tool,
    get_article_tool,
    follow_references_tool,
    tinh_tro_cap_thoi_viec_tool,
    tinh_tro_cap_mat_viec_tool,
    tinh_tien_lam_them_gio_tool,
    tinh_ngay_phep_nam_tool,
    tinh_thoi_han_bao_truoc_tool,
    ask_user,
]
