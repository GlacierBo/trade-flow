"""股票相关数据传输对象"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StockData(BaseModel):
    """股票行情数据"""
    code: str = ""
    name: str = "---"
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
    source: str = "eastmoney"
    created_at: Optional[datetime] = None


class BatchQueryRequest(BaseModel):
    """批量查询请求"""
    codes: list[str]
