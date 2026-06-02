import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PortfolioItem
from app.schemas import ApiResponse, CreatePortfolioItemRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("")
def get_portfolio_items(user_id: int = 1, db: Session = Depends(get_db)):
    """获取所有持仓比例项目"""
    try:
        items = db.query(PortfolioItem).filter(
            PortfolioItem.user_id == user_id
        ).order_by(PortfolioItem.created_at.desc()).all()

        data = [{
            "id": item.id,
            "name": item.name,
            "contract": item.contract,
            "tag": item.tag,
            "price": float(item.price),
            "user_id": item.user_id,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        } for item in items]

        return ApiResponse(data=data)
    except Exception as e:
        logger.error("加载持仓项目失败: %s", e)
        return ApiResponse(success=False, error="加载持仓项目失败")


@router.post("")
def create_portfolio_item(body: CreatePortfolioItemRequest, db: Session = Depends(get_db)):
    """创建持仓比例项目（如果合约已存在，累加价格）"""
    try:
        # 查询是否已有同合约记录
        existing = db.query(PortfolioItem).filter(
            PortfolioItem.contract == body.contract,
            PortfolioItem.user_id == body.user_id
        ).first()

        if existing:
            # 累加价格
            existing.price += body.price
            existing.name = body.name
            if body.tag:
                existing.tag = body.tag
            db.commit()
            return ApiResponse(data={
                "id": existing.id,
                "name": existing.name,
                "contract": existing.contract,
                "tag": existing.tag,
                "price": float(existing.price),
                "user_id": existing.user_id,
                "created_at": existing.created_at.isoformat() if existing.created_at else None,
            })

        item = PortfolioItem(
            name=body.name,
            contract=body.contract,
            tag=body.tag,
            price=body.price,
            user_id=body.user_id
        )
        db.add(item)
        db.commit()

        return ApiResponse(data={
            "id": item.id,
            "name": item.name,
            "contract": item.contract,
            "tag": item.tag,
            "price": float(item.price),
            "user_id": item.user_id,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        })
    except Exception as e:
        db.rollback()
        logger.error("创建持仓项目失败: %s", e)
        return ApiResponse(success=False, error=str(e) or "保存失败")


@router.delete("/{item_id}")
def delete_portfolio_item(item_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """删除持仓比例项目"""
    try:
        item = db.query(PortfolioItem).filter(
            PortfolioItem.id == item_id,
            PortfolioItem.user_id == user_id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="持仓项目不存在")

        db.delete(item)
        db.commit()

        return ApiResponse(data={"status": "success"})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("删除持仓项目失败: %s", e)
        return ApiResponse(success=False, error=str(e) or "删除失败")
