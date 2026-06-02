"""数据传输对象模块"""
from app.schemas.common import ApiResponse
from app.schemas.stock import StockData, BatchQueryRequest
from app.schemas.watchlist import WatchlistItem, WatchlistWithQuote, AddWatchlistRequest
from app.schemas.trade import CreateTradeRequest, DeleteTradeRequest, TradeResponse
from app.schemas.position import UpdatePositionPriceRequest, PositionResponse
from app.schemas.portfolio import CreatePortfolioItemRequest, PortfolioItemResponse
from app.schemas.trade_tag import UpsertTradeTagRequest, TradeTagResponse
from app.schemas.contract import CreateContractRequest, UpdateContractRequest, ContractResponse
from app.schemas.auth import (
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
