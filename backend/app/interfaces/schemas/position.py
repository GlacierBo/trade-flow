"""持仓相关数据传输对象"""
from typing import Optional

from pydantic import BaseModel


class UpdatePositionPriceRequest(BaseModel):
    """更新持仓价格请求"""
    price: float
    user_id: int = 1


class PositionResponse(BaseModel):
    """持仓响应"""
    id: int
    contract: str
    name: str
    user_id: int
    total_shares: int
    avg_cost: float
    latest_price: float
    market_value: float
    profit: float
    profit_rate: float
    updated_at: Optional[str]
