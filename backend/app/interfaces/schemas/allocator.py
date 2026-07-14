"""持仓分配器相关数据传输对象"""
from typing import Optional

from pydantic import BaseModel


class CreateAllocatorPositionRequest(BaseModel):
    """创建持仓分配器项目请求"""
    variety: str = ""
    contract_code: str
    contract_name: str = ""
    price: float = 0
    amount: float = 0
    color: str = ""
    user_id: int = 1


class UpdateAllocatorPositionRequest(BaseModel):
    """更新持仓分配器项目请求"""
    variety: Optional[str] = None
    contract_code: Optional[str] = None
    contract_name: Optional[str] = None
    price: Optional[float] = None
    amount: Optional[float] = None
    color: Optional[str] = None


class AllocatorPositionResponse(BaseModel):
    """持仓分配器项目响应"""
    id: int
    variety: str
    contract_code: str
    contract_name: str
    price: float
    amount: float
    color: str
    user_id: int
    created_at: Optional[str]
