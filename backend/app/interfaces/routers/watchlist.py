import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.interfaces.schemas import AddWatchlistRequest, ApiResponse
from app.application.services import market, watchlist as wl_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("")
def get_watchlist(db: Session = Depends(get_db)):
    data = wl_service.get_watchlist(db)
    return ApiResponse(data=data)


@router.post("")
async def add_watchlist(body: AddWatchlistRequest, db: Session = Depends(get_db)):
    code = body.code
    name = body.name or code

    stock = await market.get_stock(code, db)
    if stock and stock.get("name") and stock["name"] != "---":
        name = stock["name"]

    wl_service.add_watchlist(db, code, name)
    return ApiResponse(data={"code": code, "name": name})


@router.delete("/{code}")
def remove_watchlist(code: str, db: Session = Depends(get_db)):
    wl_service.remove_watchlist(db, code)
    return ApiResponse(data=None)


@router.post("/refresh")
async def refresh_watchlist(db: Session = Depends(get_db)):
    data = await wl_service.refresh_watchlist(db)
    return ApiResponse(data=data)
