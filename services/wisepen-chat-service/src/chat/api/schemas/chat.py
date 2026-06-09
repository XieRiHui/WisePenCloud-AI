from typing import Optional, List, Dict, Any, Set
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    聊天请求传输对象
    """
    session_id: str = Field(..., description="会话ID")
    query: str = Field(..., description="用户问题")
    model: Optional[str] = Field(default=None, description="模型ID")
    provider_id: Optional[str] = Field(default=None, description="指定供应商ID")
    states: Optional[List[Dict[str, Any]]] = Field(default=None, description="上下文状态列表")
    self_selectable_skill_ids: Optional[Set[str]] = Field(default=None, description="本轮暴露给 LLM 自动选择的 Skill 资源 ID 列表")
    model_config = {"extra": "ignore"}
