from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ApiResponse, BatchQueryRequest
from app.services import market

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/search")
async def search_stocks(
    q: str = Query(""),
    source: str = Query("auto", description="数据源: auto/sina/eastmoney"),
):
    if not q:
        return ApiResponse(success=False, error="Missing q")
    stocks = await market.search_stocks(q, source)
    return ApiResponse(data=stocks)


@router.post("/batch")
async def batch_query(body: BatchQueryRequest):
    stocks = await market.get_stocks(body.codes)
    return ApiResponse(data=stocks)


@router.get("/{code}")
async def get_stock(code: str, db: Session = Depends(get_db)):
    stock = await market.get_stock(code, db)
    return ApiResponse(data=stock)
