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


# ============================================
# 交易相关 Schemas
# ============================================

class CreateTradeRequest(BaseModel):
    contract: str
    name: str
    price: float
    shares: int
    fee_rate: float = 0.0002
    min_fee: float = 0.2
    buy_order_no: Optional[str] = None  # 卖出时必填
    user_id: int = 1


class DeleteTradeRequest(BaseModel):
    user_id: int = 1


class TradeResponse(BaseModel):
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


# ============================================
# 持仓相关 Schemas
# ============================================

class UpdatePositionPriceRequest(BaseModel):
    price: float
    user_id: int = 1


class PositionResponse(BaseModel):
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


# ============================================
# 持仓比例相关 Schemas
# ============================================

class CreatePortfolioItemRequest(BaseModel):
    name: str
    contract: str
    tag: str = ""
    price: float
    user_id: int = 1


class PortfolioItemResponse(BaseModel):
    id: int
    name: str
    contract: str
    tag: str
    price: float
    user_id: int
    created_at: Optional[str]


# ============================================
# 交易标签相关 Schemas
# ============================================

class UpsertTradeTagRequest(BaseModel):
    contract: str
    name: str
    user_id: int = 1


class TradeTagResponse(BaseModel):
    id: int
    contract: str
    name: str
    latest_price: float
    user_id: int
    updated_at: Optional[str]


# ============================================
# 合约管理相关 Schemas
# ============================================

class CreateContractRequest(BaseModel):
    code: str
    name: str
    user_id: int = 1


class UpdateContractRequest(BaseModel):
    code: str
    name: str
    user_id: int = 1


class ContractResponse(BaseModel):
    id: int
    code: str
    name: str
    user_id: int
    created_at: Optional[str] = None


# ============================================
# 用户认证相关 Schemas
# ============================================

class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str


class ChangePasswordRequest(BaseModel):
    user_id: int
    old_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    user_id: int


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: Optional[str]
