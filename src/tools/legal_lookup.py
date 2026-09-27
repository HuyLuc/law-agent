"""Cong cu tra cuu van ban luat cho agent.

Docstring cua moi ham duoc LLM doc de quyet dinh khi nao goi cong cu nao,
nen viet ro rang, cu the.
"""

from qdrant_client import models

from src.config import settings
from src.retrieval.hybrid import get_client
from src.retrieval.reranker import search_reranked


def search_law(query: str, van_ban: str | None = None) -> list[dict]:
    """Tim kiem dieu luat theo ngu nghia (dung khi chua biet chinh xac so Dieu).

    Dung V3 (hybrid dense+sparse + rerank) cua Tuan 2, tra ve toi da 5 chunk
    lien quan nhat. Moi chunk co day du "id", "van_ban", "so_hieu", "dieu",
    "khoan", "tieu_de_dieu", "noi_dung", "dan_chieu".

    Args:
        query: Cau hoi hoac tu khoa can tim (tieng Viet).
        van_ban: Neu biet truoc chi muon tim trong 1 van ban cu the, truyen
            dung ten day du nhu trong truong "van_ban" cua chunk (vi du:
            "Bộ luật Lao động 2019"). De None de tim tren tat ca van ban.

    Returns:
        Danh sach toi da 5 chunk, sap xep theo do lien quan giam dan.
    """
    return search_reranked(query, top_k=5, van_ban=van_ban)


def get_article(van_ban: str, dieu: int, khoan: int | None = None) -> list[dict]:
    """Tra chinh xac 1 Dieu (hoac 1 Khoan) theo metadata, KHONG tim ngu nghia.

    Dung khi da biet chinh xac so Dieu can tra (vi du agent da thay "Điều 46"
    duoc dan chieu trong ket qua search_law truoc do, hoac nguoi dung hoi
    thang "Điều X của Y quy định gì"). Ket qua chinh xac 100%, khong bi anh
    huong boi chat luong tim kiem ngu nghia.

    Args:
        van_ban: Ten van ban (vi du "Bộ luật Lao động 2019") hoac so hieu
            (vi du "45/2019/QH14") -- khop voi ca 2 truong nay trong du lieu.
        dieu: So Dieu can tra (vi du 46).
        khoan: So Khoan can tra. Neu None, tra ve TAT CA cac chunk con cua
            Dieu do (mot Dieu dai co the duoc chia thanh nhieu chunk theo
            Khoan trong buoc xu ly du lieu).

    Returns:
        Danh sach chunk khop (thuong la 1 chunk; co the nhieu neu Dieu bi
        chia theo Khoan va khoan=None). Danh sach rong neu khong tim thay.
    """
    must: list[models.Condition] = [
        models.Filter(
            should=[
                models.FieldCondition(key="so_hieu", match=models.MatchValue(value=van_ban)),
                models.FieldCondition(key="van_ban", match=models.MatchValue(value=van_ban)),
            ]
        ),
        models.FieldCondition(key="dieu", match=models.MatchValue(value=dieu)),
    ]
    if khoan is not None:
        must.append(models.FieldCondition(key="khoan", match=models.MatchValue(value=khoan)))

    records, _next_offset = get_client().scroll(
        collection_name=settings.QDRANT_COLLECTION,
        scroll_filter=models.Filter(must=must),
        limit=50,
    )
    chunks = [r.payload for r in records]
    chunks.sort(key=lambda c: c["khoan"] or 0)
    return chunks


def follow_references(chunk_id: str) -> list[dict]:
    """Tra tiep cac Dieu duoc dan chieu boi 1 chunk (truong "dan_chieu").

    Dung sau khi search_law hoac get_article tra ve 1 chunk co nhac den
    Dieu khac (vi du noi dung co cau "theo quy dinh tai Điều 34 của Bộ luật
    này"), va agent can doc them noi dung Dieu do de tra loi day du. Cac
    Dieu duoc dan chieu duoc gia dinh nam trong CUNG van ban voi chunk goc.

    Args:
        chunk_id: Truong "id" cua chunk goc (vi du "BLLD2019_D45_K0").

    Returns:
        Danh sach chunk cua tat ca cac Dieu trong "dan_chieu" cua chunk goc.
        Danh sach rong neu khong tim thay chunk goc hoac khong co dan chieu.
    """
    records, _next_offset = get_client().scroll(
        collection_name=settings.QDRANT_COLLECTION,
        scroll_filter=models.Filter(
            must=[models.FieldCondition(key="id", match=models.MatchValue(value=chunk_id))]
        ),
        limit=1,
    )
    if not records:
        return []
    source = records[0].payload
    referenced_chunks: list[dict] = []
    for dieu in source.get("dan_chieu") or []:
        referenced_chunks.extend(get_article(source["so_hieu"], dieu))
    return referenced_chunks
