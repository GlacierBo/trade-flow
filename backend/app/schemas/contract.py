"""合约管理相关数据传输对象"""
from typing import Optional

from pydantic import BaseModel


class CreateContractRequest(BaseModel):
    """创建合约请求"""
    code: str
    name: str
    user_id: int = 1


class UpdateContractRequest(BaseModel):
    """更新合约请求"""
    code: str
    name: str
    user_id: int = 1


class ContractResponse(BaseModel):
    """合约响应"""
    id: int
    code: str
    name: str
    user_id: int
    created_at: Optional[str] = None
