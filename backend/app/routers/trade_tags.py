import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TradeTag
from app.schemas import ApiResponse, UpsertTradeTagRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trade-tags", tags=["trade-tags"])


@router.get("")
def get_trade_tags(user_id: int = 1, db: Session = Depends(get_db)):
    """获取所有交易标签"""
    try:
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
    except Exception as e:
        logger.error("加载交易标签失败: %s", e)
        return ApiResponse(success=False, error="加载交易标签失败")


@router.post("")
def upsert_trade_tag(body: UpsertTradeTagRequest, db: Session = Depends(get_db)):
    """创建或更新交易标签"""
    try:
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
    except Exception as e:
        db.rollback()
        logger.error("更新标签失败: %s", e)
        return ApiResponse(success=False, error=str(e))


@router.delete("/{tag_id}")
def delete_trade_tag(tag_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """删除交易标签"""
    try:
        tag = db.query(TradeTag).filter(
            TradeTag.id == tag_id,
            TradeTag.user_id == user_id
        ).first()

        if not tag:
            raise HTTPException(status_code=404, detail="标签不存在")

        db.delete(tag)
        db.commit()

        return ApiResponse(data={"status": "success"})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("删除标签失败: %s", e)
        return ApiResponse(success=False, error=str(e) or "删除失败")
