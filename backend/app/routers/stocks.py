from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ApiResponse, BatchQueryRequest
from app.services import market

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/search")
async def search_stocks(q: str = Query("")):
    if not q:
        return ApiResponse(success=False, error="Missing q")
    try:
        stocks = await market.search_stocks(q)
        return ApiResponse(data=stocks)
    except Exception as e:
        return ApiResponse(success=False, error="行情服务暂不可用，请稍后重试")


@router.post("/batch")
async def batch_query(body: BatchQueryRequest):
    try:
        stocks = await market.get_stocks(body.codes)
        return ApiResponse(data=stocks)
    except Exception as e:
        return ApiResponse(success=False, error="行情服务暂不可用，请稍后重试")


@router.get("/{code}")
async def get_stock(code: str, db: Session = Depends(get_db)):
    try:
        stock = await market.get_stock(code, db)
        return ApiResponse(data=stock)
    except Exception as e:
        return ApiResponse(success=False, error="行情服务暂不可用，请稍后重试")
