"""State cua LangGraph agent."""

from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    route: Literal["legal_qa", "contract", "out_of_scope"]
    user_profile: dict  # loai HD, tham nien, luong, vung... (agent tu dien)
    evidence: dict[str, str]  # chunk_id (hoac "can_cu:<Dieu X>") -> noi dung
    tool_calls_count: int
    verify_rounds: int


class RouteDecision(BaseModel):
    route: Literal["legal_qa", "contract", "out_of_scope"] = Field(
        description=(
            "'legal_qa' cho cau hoi ve luat lao dong (tra cuu, tinh toan, tinh huong); "
            "'contract' khi nguoi dung muon ra soat/kiem tra mot hop dong lao dong cu the; "
            "'out_of_scope' khi cau hoi khong lien quan Luat Lao dong Viet Nam"
        )
    )
    ly_do: str = Field(description="Giai thich ngan gon vi sao chon route nay")
