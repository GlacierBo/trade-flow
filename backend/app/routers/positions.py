import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Position, Trade
from app.schemas import ApiResponse, UpdatePositionPriceRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/positions", tags=["positions"])


@router.get("")
def get_positions(user_id: int = 1, db: Session = Depends(get_db)):
    """获取所有持仓"""
    try:
        positions = db.query(Position).filter(
            Position.user_id == user_id
        ).order_by(Position.updated_at.desc()).all()

        data = [{
            "id": p.id,
            "contract": p.contract,
            "name": p.name,
            "user_id": p.user_id,
            "total_shares": p.total_shares,
            "avg_cost": float(p.avg_cost),
            "latest_price": float(p.latest_price),
            "market_value": float(p.market_value),
            "profit": float(p.profit),
            "profit_rate": float(p.profit_rate),
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        } for p in positions]

        return ApiResponse(data=data)
    except Exception as e:
        logger.error("加载持仓失败: %s", e)
        return ApiResponse(success=False, error="加载持仓失败")


@router.put("/{position_id}/price")
def update_position_price(
    position_id: int,
    body: UpdatePositionPriceRequest,
    db: Session = Depends(get_db)
):
    """更新持仓最新价格"""
    try:
        position = db.query(Position).filter(
            Position.id == position_id,
            Position.user_id == body.user_id
        ).first()

        if not position:
            raise HTTPException(status_code=404, detail="持仓不存在")

        # 更新价格、市值、盈亏
        market_value = position.total_shares * body.price
        unrealized_profit = (body.price - float(position.avg_cost)) * position.total_shares
        profit_rate = (
            (unrealized_profit / (float(position.avg_cost) * position.total_shares) * 100)
            if position.avg_cost > 0 else 0
        )

        position.latest_price = body.price
        position.market_value = market_value
        position.profit_rate = profit_rate

        db.commit()

        return ApiResponse(data={"status": "success"})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("更新价格失败: %s", e)
        return ApiResponse(success=False, error="更新价格失败")


@router.delete("/{position_id}")
def clear_position(position_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """清仓"""
    try:
        position = db.query(Position).filter(
            Position.id == position_id,
            Position.user_id == user_id
        ).first()

        if not position:
            raise HTTPException(status_code=404, detail="持仓不存在")

        # 删除该合约的所有交易记录
        db.query(Trade).filter(
            Trade.contract == position.contract,
            Trade.user_id == user_id
        ).delete()

        # 删除持仓记录
        db.delete(position)
        db.commit()

        return ApiResponse(data={"status": "success"})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("清仓失败: %s", e)
        return ApiResponse(success=False, error="清仓失败")
