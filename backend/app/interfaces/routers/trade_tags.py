from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.domain.models import TradeTag
from app.interfaces.schemas import ApiResponse, UpsertTradeTagRequest, BatchTradeTagRequest

router = APIRouter(prefix="/api/trade-tags", tags=["trade-tags"])


@router.get("")
def get_trade_tags(user_id: int = 1, db: Session = Depends(get_db)):
    """获取所有交易标签"""
    tags = db.query(TradeTag).filter(
        TradeTag.user_id == user_id
    ).order_by(TradeTag.updated_at.desc()).all()

    data = [{
        "id": tag.id,
        "contract": tag.contract,
        "name": tag.name,
        "latest_price": float(tag.latest_price),
        "user_id": tag.user_id,
        "updated_at": tag.updated_at.isoformat() if tag.updated_at else None,
    } for tag in tags]

    return ApiResponse(data=data)


@router.post("")
def upsert_trade_tag(body: UpsertTradeTagRequest, db: Session = Depends(get_db)):
    """创建或更新交易标签"""
    existing = db.query(TradeTag).filter(
        TradeTag.contract == body.contract,
        TradeTag.user_id == body.user_id
    ).first()

    if existing:
        existing.name = body.name
    else:
        db.add(TradeTag(
            contract=body.contract,
            name=body.name,
            latest_price=0,
            user_id=body.user_id
        ))

    db.commit()
    return ApiResponse(data={"status": "success"})


@router.put("/batch")
def batch_replace_trade_tags(body: BatchTradeTagRequest, db: Session = Depends(get_db)):
    """批量替换交易标签（先删后插）"""
    db.query(TradeTag).filter(TradeTag.user_id == body.user_id).delete()
    for item in body.items:
        db.add(TradeTag(
            contract=item.contract,
            name=item.name,
            latest_price=0,
            user_id=body.user_id,
        ))
    db.commit()
    return ApiResponse(data={"status": "success", "count": len(body.items)})


@router.delete("/{tag_id}")
def delete_trade_tag(tag_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """删除交易标签"""
    tag = db.query(TradeTag).filter(
        TradeTag.id == tag_id,
        TradeTag.user_id == user_id
    ).first()

    if not tag:
        return ApiResponse(success=False, error="标签不存在")

    db.delete(tag)
    db.commit()

    return ApiResponse(data={"status": "success"})
