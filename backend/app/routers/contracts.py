import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.contract import Contract
from app.schemas import ApiResponse, CreateContractRequest, UpdateContractRequest, ContractResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


@router.get("")
def get_contracts(user_id: int = 1, db: Session = Depends(get_db)):
    """获取合约列表"""
    try:
        contracts = db.query(Contract).filter(Contract.user_id == user_id).order_by(Contract.created_at.desc()).all()
        data = [
            ContractResponse(
                id=c.id,
                code=c.code,
                name=c.name,
                user_id=c.user_id,
                created_at=str(c.created_at) if c.created_at else None,
            )
            for c in contracts
        ]
        return ApiResponse(data=data)
    except Exception as e:
        logger.error("getContracts error: %s", e)
        return ApiResponse(data=[])


@router.post("")
def add_contract(body: CreateContractRequest, db: Session = Depends(get_db)):
    """新增合约"""
    try:
        exists = db.query(Contract).filter(
            Contract.user_id == body.user_id,
            Contract.code == body.code,
        ).first()
        if exists:
            return ApiResponse(success=False, error="合约代码已存在")

        contract = Contract(code=body.code, name=body.name, user_id=body.user_id)
        db.add(contract)
        db.commit()
        db.refresh(contract)

        return ApiResponse(data=ContractResponse(
            id=contract.id,
            code=contract.code,
            name=contract.name,
            user_id=contract.user_id,
            created_at=str(contract.created_at) if contract.created_at else None,
        ))
    except Exception as e:
        db.rollback()
        logger.error("addContract error: %s", e)
        return ApiResponse(success=False, error=str(e))


@router.put("/{old_code}")
def update_contract(old_code: str, body: UpdateContractRequest, db: Session = Depends(get_db)):
    """编辑合约"""
    try:
        contract = db.query(Contract).filter(
            Contract.user_id == body.user_id,
            Contract.code == old_code,
        ).first()
        if not contract:
            return ApiResponse(success=False, error="合约不存在")

        # 如果改了 code，检查新 code 是否冲突
        if old_code != body.code:
            exists = db.query(Contract).filter(
                Contract.user_id == body.user_id,
                Contract.code == body.code,
            ).first()
            if exists:
                return ApiResponse(success=False, error="新合约代码已存在")

        contract.code = body.code
        contract.name = body.name
        db.commit()

        return ApiResponse(data=ContractResponse(
            id=contract.id,
            code=contract.code,
            name=contract.name,
            user_id=contract.user_id,
            created_at=str(contract.created_at) if contract.created_at else None,
        ))
    except Exception as e:
        db.rollback()
        logger.error("updateContract error: %s", e)
        return ApiResponse(success=False, error=str(e))


@router.delete("/{code}")
def delete_contract(code: str, user_id: int = 1, db: Session = Depends(get_db)):
    """删除合约"""
    try:
        contract = db.query(Contract).filter(
            Contract.user_id == user_id,
            Contract.code == code,
        ).first()
        if not contract:
            return ApiResponse(success=False, error="合约不存在")

        db.delete(contract)
        db.commit()
        return ApiResponse(data=None)
    except Exception as e:
        db.rollback()
        logger.error("deleteContract error: %s", e)
        return ApiResponse(success=False, error=str(e))
