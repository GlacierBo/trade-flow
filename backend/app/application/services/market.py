"""行情查询服务 —— 协调 provider 与数据库"""

from sqlalchemy.orm import Session

from app.domain.models import Stock, Watchlist
from app.infrastructure.clients import auto, sina, eastmoney, tencent
from app.application.services.helpers import to_float


async def search_stocks(keyword: str, source: str = "auto") -> list[dict]:
    """搜索股票，支持指定数据源"""
    if source == "sina":
        return await sina.search_stocks(keyword)
    elif source == "tencent":
        return await tencent.search_stocks(keyword)
    elif source == "eastmoney":
        return await eastmoney.search_stocks(keyword)
    else:
        return await auto.search_stocks(keyword)


async def get_stock(code: str, db: Session) -> dict | None:
    """查单只股票：优先 DB，DB 没有则调 API 并存入 DB"""
    row = (
        db.query(Stock)
        .filter(Stock.code == code)
        .order_by(Stock.created_at.desc())
        .first()
    )
    if row:
        return _row_to_dict(row)

    stock = await auto.get_stock(code)
    if stock and stock.get("name") and stock["name"] != "---":
        stock["code"] = code
        _insert_stock(db, stock)
    return stock


async def get_stocks(codes: list[str]) -> list[dict]:
    return await auto.get_stocks(codes)


def _insert_stock(db: Session, stock: dict):
    row = Stock(
        code=stock.get("code"),
        name=stock.get("name"),
        price=stock.get("price"),
        changePercent=stock.get("changePercent"),
        open=stock.get("open"),
        high=stock.get("high"),
        low=stock.get("low"),
        yesterday=stock.get("yesterday"),
        volume=stock.get("volume"),
        amount=stock.get("amount"),
        amplitude=stock.get("amplitude"),
        turnoverRate=stock.get("turnoverRate"),
        totalMarketCap=stock.get("totalMarketCap"),
        source=stock.get("source", "eastmoney"),
    )
    db.add(row)
    db.commit()


def insert_stock(db: Session, stock: dict):
    _insert_stock(db, stock)


def _row_to_dict(row: Stock) -> dict:
    return {
        "code": row.code,
        "name": row.name,
        "price": to_float(row.price),
        "changePercent": to_float(row.changePercent),
        "open": to_float(row.open),
        "high": to_float(row.high),
        "low": to_float(row.low),
        "yesterday": to_float(row.yesterday),
        "volume": to_float(row.volume),
        "amount": to_float(row.amount),
        "amplitude": to_float(row.amplitude),
        "turnoverRate": to_float(row.turnoverRate),
        "totalMarketCap": to_float(row.totalMarketCap),
        "source": row.source,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }
