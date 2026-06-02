import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AddWatchlistRequest, ApiResponse
from app.services import market, watchlist as wl_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("")
def get_watchlist(db: Session = Depends(get_db)):
    try:
        data = wl_service.get_watchlist(db)
        return ApiResponse(data=data)
    except Exception as e:
        logger.error("getWatchlist error: %s", e)
        return ApiResponse(data=[])


@router.post("")
async def add_watchlist(body: AddWatchlistRequest, db: Session = Depends(get_db)):
    code = body.code
    name = body.name or code

    try:
        stock = await market.get_stock(code, db)
        if stock and stock.get("name") and stock["name"] != "---":
            name = stock["name"]
    except Exception as e:
        logger.error("fetch stock error: %s", e)

    try:
        wl_service.add_watchlist(db, code, name)
    except Exception as e:
        logger.error("addWatchlist error: %s", e)

    return ApiResponse(data={"code": code, "name": name})


@router.delete("/{code}")
def remove_watchlist(code: str, db: Session = Depends(get_db)):
    try:
        wl_service.remove_watchlist(db, code)
    except Exception as e:
        logger.error("removeWatchlist error: %s", e)
    return ApiResponse(data=None)


@router.post("/refresh")
async def refresh_watchlist(db: Session = Depends(get_db)):
    try:
        data = await wl_service.refresh_watchlist(db)
        return ApiResponse(data=data)
    except Exception as e:
        logger.error("refresh error: %s", e)
        return ApiResponse(data=[])
