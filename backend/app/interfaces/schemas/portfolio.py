"""持仓比例相关数据传输对象"""
from typing import Optional

from pydantic import BaseModel


class CreatePortfolioItemRequest(BaseModel):
    """创建持仓比例项目请求"""
    name: str
    contract: str
    tag: str = ""
    price: float
    user_id: int = 1


class PortfolioItemResponse(BaseModel):
    """持仓比例项目响应"""
    id: int
    name: str
    contract: str
    tag: str
    price: float
    user_id: int
    created_at: Optional[str]
