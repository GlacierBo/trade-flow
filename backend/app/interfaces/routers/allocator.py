from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.domain.models import AllocatorPosition
from app.interfaces.schemas import ApiResponse
from app.interfaces.schemas.allocator import CreateAllocatorPositionRequest, UpdateAllocatorPositionRequest

router = APIRouter(prefix="/api/allocator", tags=["allocator"])


def _format_position(p: AllocatorPosition) -> dict:
    return {
        "id": p.id,
        "variety": p.variety or "",
        "contract_code": p.contract_code or "",
        "contract_name": p.contract_name or "",
        "price": float(p.price),
        "amount": float(p.amount),
        "color": p.color or "",
        "user_id": p.user_id,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


@router.get("")
def get_allocator_positions(user_id: int = 1, db: Session = Depends(get_db)):
    """获取所有分配器持仓"""
    items = db.query(AllocatorPosition).filter(
        AllocatorPosition.user_id == user_id
    ).order_by(AllocatorPosition.created_at.desc()).all()

    return ApiResponse(data=[_format_position(item) for item in items])


@router.post("")
def create_allocator_position(body: CreateAllocatorPositionRequest, db: Session = Depends(get_db)):
    """创建分配器持仓"""
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

    return ApiResponse(data=_format_position(item))


@router.put("/{position_id}")
def update_allocator_position(position_id: int, body: UpdateAllocatorPositionRequest, user_id: int = 1, db: Session = Depends(get_db)):
    """更新分配器持仓"""
    item = db.query(AllocatorPosition).filter(
        AllocatorPosition.id == position_id,
        AllocatorPosition.user_id == user_id
    ).first()

    if not item:
        return ApiResponse(success=False, error="分配器持仓不存在")

    if body.variety is not None:
        item.variety = body.variety
    if body.contract_code is not None:
        item.contract_code = body.contract_code
    if body.contract_name is not None:
        item.contract_name = body.contract_name
    if body.price is not None:
        item.price = body.price
    if body.amount is not None:
        item.amount = body.amount
    if body.color is not None:
        item.color = body.color

    db.commit()

    return ApiResponse(data=_format_position(item))


@router.delete("/{position_id}")
def delete_allocator_position(position_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """删除分配器持仓"""
    item = db.query(AllocatorPosition).filter(
        AllocatorPosition.id == position_id,
        AllocatorPosition.user_id == user_id
    ).first()

    if not item:
        return ApiResponse(success=False, error="分配器持仓不存在")

    db.delete(item)
    db.commit()

    return ApiResponse(data={"status": "success"})
