"""Cac phien ban tra loi cau hoi (V0-V4), dung de danh gia trong Tuan 4.

V0 la moc so sanh: hoi thang LLM, khong tra cuu, khong cong cu. Cac phien
ban con lai duoc them dan o Tuan 3 khi da co calculators/legal_lookup/agent.
"""

from src.llm import invoke_with_fallback

V0_SYSTEM_PROMPT = (
    "Ban la tro ly tra loi cau hoi ve Luat Lao dong Viet Nam. Tra loi ngan gon, "
    "chinh xac nhat co the. Cuoi cau tra loi ghi ro: 'Noi dung chi mang tinh tham "
    "khao, khong thay the tu van phap ly.'"
)


def answer_v0(question: str) -> str:
    prompt = f"{V0_SYSTEM_PROMPT}\n\nCau hoi: {question}"
    return invoke_with_fallback(prompt).content
