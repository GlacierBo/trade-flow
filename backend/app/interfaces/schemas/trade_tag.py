"""交易标签相关数据传输对象"""
from typing import Optional, List

from pydantic import BaseModel


class UpsertTradeTagRequest(BaseModel):
    """创建或更新交易标签请求"""
    contract: str
    name: str
    user_id: int = 1


class TradeTagResponse(BaseModel):
    """交易标签响应"""
    id: int
    contract: str
    name: str
    latest_price: float
    user_id: int
    updated_at: Optional[str]


class BatchTradeTagItem(BaseModel):
    """批量替换中的单条标签"""
    contract: str
    name: str


class BatchTradeTagRequest(BaseModel):
    """批量替换交易标签请求"""
    items: List[BatchTradeTagItem]
    user_id: int = 1
