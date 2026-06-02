from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StockData(BaseModel):
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


class WatchlistItem(BaseModel):
    code: str
    name: str
    added_at: Optional[datetime] = None


class WatchlistWithQuote(WatchlistItem):
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


class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[object] = None
    error: Optional[str] = None


class AddWatchlistRequest(BaseModel):
    code: str
    name: Optional[str] = None


class BatchQueryRequest(BaseModel):
    codes: list[str]
