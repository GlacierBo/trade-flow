from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.domain.models import AllocatorPosition
from app.interfaces.schemas import ApiResponse
from app.interfaces.schemas.allocator import (
    CreateAllocatorPositionRequest,
    UpdateAllocatorPositionRequest,
)

router = APIRouter(prefix="/api/allocator", tags=["allocator"])


def _to_dict(item: AllocatorPosition) -> dict:
    return {
        "id": item.id,
        "variety": item.variety,
        "contract_code": item.contract_code,
        "contract_name": item.contract_name,
        "price": float(item.price),
        "amount": float(item.amount),
        "color": item.color,
        "user_id": item.user_id,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


@router.get("")
def get_allocator_positions(user_id: int = Query(1), db: Session = Depends(get_db)):
    """获取所有持仓分配器项目"""
    items = db.query(AllocatorPosition).filter(
        AllocatorPosition.user_id == user_id
    ).order_by(AllocatorPosition.created_at.asc()).all()
    return ApiResponse(data=[_to_dict(item) for item in items])


@router.post("")
def create_allocator_position(body: CreateAllocatorPositionRequest, db: Session = Depends(get_db)):
    """创建持仓分配器项目"""
    item = AllocatorPosition(
        variety=body.variety,
        contract_code=body.contract_code,
        contract_name=body.contract_name,
        price=body.price,
        amount=body.amount,
        color=body.color,
        user_id=body.user_id,
    )
    db.add(item)
    db.commit()
    return ApiResponse(data=_to_dict(item))


@router.put("/{item_id}")
def update_allocator_position(
    item_id: int,
    body: UpdateAllocatorPositionRequest,
    user_id: int = Query(1),
    db: Session = Depends(get_db),
):
    """更新持仓分配器项目"""
    item = db.query(AllocatorPosition).filter(
        AllocatorPosition.id == item_id,
        AllocatorPosition.user_id == user_id,
    ).first()
    if not item:
        return ApiResponse(success=False, error="项目不存在")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    db.commit()
    return ApiResponse(data=_to_dict(item))


@router.delete("/{item_id}")
def delete_allocator_position(item_id: int, user_id: int = Query(1), db: Session = Depends(get_db)):
    """删除持仓分配器项目"""
    item = db.query(AllocatorPosition).filter(
        AllocatorPosition.id == item_id,
        AllocatorPosition.user_id == user_id,
    ).first()
    if not item:
        return ApiResponse(success=False, error="项目不存在")
    db.delete(item)
    db.commit()
    return ApiResponse(data={"status": "success"})
