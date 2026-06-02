"""行情查询服务 —— 协调 provider 与数据库"""

from sqlalchemy.orm import Session

from app.models import Stock, Watchlist
from clients import auto


async def search_stocks(keyword: str) -> list[dict]:
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
        "price": _d(row.price),
        "changePercent": _d(row.changePercent),
        "open": _d(row.open),
        "high": _d(row.high),
        "low": _d(row.low),
        "yesterday": _d(row.yesterday),
        "volume": _d(row.volume),
        "amount": _d(row.amount),
        "amplitude": _d(row.amplitude),
        "turnoverRate": _d(row.turnoverRate),
        "totalMarketCap": _d(row.totalMarketCap),
        "source": row.source,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def _d(val) -> float | None:
    return float(val) if val is not None else None
