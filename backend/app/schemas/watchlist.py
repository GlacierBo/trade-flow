"""自选股相关数据传输对象"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WatchlistItem(BaseModel):
    """自选股基础信息"""
    code: str
    name: str
    added_at: Optional[datetime] = None


class WatchlistWithQuote(WatchlistItem):
    """自选股带行情数据"""
    price: Optional[float] = None
    changePercent: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    yesterday: Optional[float] = None
    volume: Optional[float] = None
    amount: Optional[float] = None
    amplitude: Optional[float] = None
    turnoverRate: Optional[float] = None
    totalMarketCap: Optional[float] = None
    source: Optional[str] = None


class AddWatchlistRequest(BaseModel):
    """添加自选股请求"""
    code: str
    name: Optional[str] = None
