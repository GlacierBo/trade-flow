"""数据传输对象模块"""
from app.interfaces.schemas.common import ApiResponse
from app.interfaces.schemas.stock import StockData, BatchQueryRequest
from app.interfaces.schemas.watchlist import WatchlistItem, WatchlistWithQuote, AddWatchlistRequest, BatchWatchlistRequest
from app.interfaces.schemas.trade import CreateTradeRequest, DeleteTradeRequest, TradeResponse, BatchTradeRequest
from app.interfaces.schemas.position import UpdatePositionPriceRequest, PositionResponse
from app.interfaces.schemas.portfolio import CreatePortfolioItemRequest, PortfolioItemResponse, BatchPortfolioRequest
from app.interfaces.schemas.trade_tag import UpsertTradeTagRequest, TradeTagResponse, BatchTradeTagRequest
from app.interfaces.schemas.contract import CreateContractRequest, UpdateContractRequest, ContractResponse, BatchContractRequest
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
    "BatchWatchlistRequest",
    # trade
    "CreateTradeRequest",
    "DeleteTradeRequest",
    "TradeResponse",
    "BatchTradeRequest",
    # position
    "UpdatePositionPriceRequest",
    "PositionResponse",
    # portfolio
    "CreatePortfolioItemRequest",
    "PortfolioItemResponse",
    "BatchPortfolioRequest",
    # trade_tag
    "UpsertTradeTagRequest",
    "TradeTagResponse",
    "BatchTradeTagRequest",
    # contract
    "CreateContractRequest",
    "UpdateContractRequest",
    "ContractResponse",
    "BatchContractRequest",
    # auth
    "LoginRequest",
    "RegisterRequest",
    "ChangePasswordRequest",
    "ResetPasswordRequest",
    "UserResponse",
]
