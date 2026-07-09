"""自选股服务"""

from sqlalchemy.orm import Session

from app.domain.models import Stock, Watchlist
from app.infrastructure.clients import auto
from app.application.services.helpers import to_float
from app.application.services.market import insert_stock


def get_watchlist(db: Session) -> list[dict]:
    """获取自选列表（含最新行情）"""
    items = db.query(Watchlist).order_by(Watchlist.added_at).all()
    if not items:
        return []

    codes = [item.code for item in items]
    latest_map = _get_latest_stocks(db, codes)

    result = []
    for item in items:
        entry = {
            "code": item.code,
            "name": item.name,
            "added_at": item.added_at.isoformat() if item.added_at else None,
        }
        latest = latest_map.get(item.code, {})
        entry.update(latest)
        result.append(entry)
    return result


def _get_latest_stocks(db: Session, codes: list[str]) -> dict[str, dict]:
    """取每个 code 的最新一条行情"""
    rows = (
        db.query(Stock)
        .filter(Stock.code.in_(codes))
        .order_by(Stock.created_at.desc())
        .all()
    )
    latest = {}
    for r in rows:
        if r.code not in latest:
            latest[r.code] = {
                "price": to_float(r.price),
                "changePercent": to_float(r.changePercent),
                "open": to_float(r.open),
                "high": to_float(r.high),
                "low": to_float(r.low),
                "yesterday": to_float(r.yesterday),
                "volume": to_float(r.volume),
                "amount": to_float(r.amount),
                "amplitude": to_float(r.amplitude),
                "turnoverRate": to_float(r.turnoverRate),
                "totalMarketCap": to_float(r.totalMarketCap),
                "source": r.source,
            }
    return latest


def add_watchlist(db: Session, code: str, name: str):
    existing = db.query(Watchlist).filter(Watchlist.code == code).first()
    if existing:
        existing.name = name
    else:
        db.add(Watchlist(code=code, name=name))
    db.commit()


def remove_watchlist(db: Session, code: str):
    db.query(Watchlist).filter(Watchlist.code == code).delete()
    db.commit()


def get_watchlist_codes(db: Session) -> list[dict]:
    rows = db.query(Watchlist.code, Watchlist.name).all()
    return [{"code": r.code, "name": r.name} for r in rows]


async def refresh_watchlist(db: Session) -> list[dict]:
    """刷新所有自选行情：调外部 API 获取最新价格，写入 DB"""
    items = get_watchlist_codes(db)
    codes = [i["code"] for i in items]
    if not codes:
        return []

    stocks = await auto.get_stocks(codes)
    for s in stocks:
        if s.get("code") and s.get("name") and s["name"] != "---":
            insert_stock(db, s)

    return get_watchlist(db)
