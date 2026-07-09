"""数据传输对象模块"""
from app.interfaces.schemas.common import ApiResponse
from app.interfaces.schemas.stock import StockData, BatchQueryRequest
from app.interfaces.schemas.watchlist import WatchlistItem, WatchlistWithQuote, AddWatchlistRequest
from app.interfaces.schemas.trade import CreateTradeRequest, DeleteTradeRequest, TradeResponse
from app.interfaces.schemas.position import UpdatePositionPriceRequest, PositionResponse
from app.interfaces.schemas.portfolio import CreatePortfolioItemRequest, PortfolioItemResponse
from app.interfaces.schemas.trade_tag import UpsertTradeTagRequest, TradeTagResponse
from app.interfaces.schemas.contract import CreateContractRequest, UpdateContractRequest, ContractResponse
from app.interfaces.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    ChangePasswordRequest,
    ResetPasswordRequest,
    UserResponse,
)

__all__ = [
    # common
    "ApiResponse",
    # stock
    "StockData",
    "BatchQueryRequest",
    # watchlist
    "WatchlistItem",
    "WatchlistWithQuote",
    "AddWatchlistRequest",
    # trade
    "CreateTradeRequest",
    "DeleteTradeRequest",
    "TradeResponse",
    # position
    "UpdatePositionPriceRequest",
    "PositionResponse",
    # portfolio
    "CreatePortfolioItemRequest",
    "PortfolioItemResponse",
    # trade_tag
    "UpsertTradeTagRequest",
    "TradeTagResponse",
    # contract
    "CreateContractRequest",
    "UpdateContractRequest",
    "ContractResponse",
    # auth
    "LoginRequest",
    "RegisterRequest",
    "ChangePasswordRequest",
    "ResetPasswordRequest",
    "UserResponse",
]
