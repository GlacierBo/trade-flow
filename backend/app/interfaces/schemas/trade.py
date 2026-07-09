"""交易相关数据传输对象"""
from typing import Optional

from pydantic import BaseModel


class CreateTradeRequest(BaseModel):
    """创建交易请求"""
    contract: str
    name: str
    price: float
    shares: int
    fee_rate: float = 0.0002
    min_fee: float = 0.2
    buy_order_no: Optional[str] = None  # 卖出时必填
    user_id: int = 1


class DeleteTradeRequest(BaseModel):
    """删除交易请求"""
    user_id: int = 1


class TradeResponse(BaseModel):
    """交易记录响应"""
    id: int
    buy_order_no: Optional[str]
    contract: str
    name: str
    price: float
    shares: int
    remaining_shares: int
    amount: float
    fee: float
    net_amount: float
    trade_type: str
    trade_date: str
    user_id: int
    created_at: Optional[str]
    realized_profit: float
    single_profit: float
    sells: list = []
