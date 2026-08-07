import logging
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.domain.models import Trade, Position
from app.interfaces.schemas import ApiResponse, CreateTradeRequest, BatchTradeRequest
from app.application.services.trades import generate_buy_order_no, recalculate_position

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trades", tags=["trades"])


@router.get("")
def get_trades(user_id: int = 1, db: Session = Depends(get_db)):
    """获取所有交易记录（按买入单号分组）"""
    all_trades = db.query(Trade).filter(
        Trade.user_id == user_id
    ).order_by(Trade.created_at.desc()).all()

    buys = []
    sell_map = {}

    for trade in all_trades:
        trade_dict = {
            "id": trade.id,
            "buy_order_no": trade.buy_order_no,
            "contract": trade.contract,
            "name": trade.name,
            "price": float(trade.price),
            "shares": trade.shares,
            "remaining_shares": trade.remaining_shares,
            "amount": float(trade.amount),
            "fee": float(trade.fee),
            "net_amount": float(trade.net_amount),
            "trade_type": trade.trade_type,
            "trade_date": str(trade.trade_date),
            "user_id": trade.user_id,
            "created_at": trade.created_at.isoformat() if trade.created_at else None,
            "realized_profit": float(trade.realized_profit),
            "single_profit": float(trade.single_profit),
        }

        if trade.trade_type == 'buy':
            trade_dict["sells"] = []
            buys.append(trade_dict)
        else:
            if trade.buy_order_no not in sell_map:
                sell_map[trade.buy_order_no] = []
            sell_map[trade.buy_order_no].append(trade_dict)

    for buy in buys:
        sells = sell_map.get(buy["buy_order_no"], [])
        sells.sort(key=lambda x: x["created_at"] or "")
        buy["sells"] = sells

    return ApiResponse(data=buys)


@router.post("")
def create_trade(body: CreateTradeRequest, db: Session = Depends(get_db)):
    """创建交易记录"""
    is_buy = body.shares > 0
    trade_date = date.today()

    if is_buy:
        order_no = generate_buy_order_no(db, trade_date)
        amount = body.price * abs(body.shares)
        fee = max(abs(amount) * body.fee_rate, body.min_fee)
        net_amount = amount + fee

        trade = Trade(
            buy_order_no=order_no,
            contract=body.contract,
            name=body.name,
            price=body.price,
            shares=body.shares,
            remaining_shares=body.shares,
            amount=amount,
            fee=fee,
            net_amount=net_amount,
            trade_type='buy',
            trade_date=trade_date,
            realized_profit=0,
            single_profit=0,
            user_id=body.user_id
        )
        db.add(trade)
        db.flush()

        recalculate_position(db, body.contract, body.user_id)
        db.commit()

        return ApiResponse(data={"status": "success", "trade_id": trade.id})
    else:
        if not body.buy_order_no:
            return ApiResponse(success=False, error="卖出操作必须提供买入单号")

        buy_record = db.query(Trade).filter(
            Trade.buy_order_no == body.buy_order_no,
            Trade.trade_type == 'buy',
            Trade.user_id == body.user_id
        ).first()

        if not buy_record:
            return ApiResponse(success=False, error="找不到对应的买入记录")

        sell_shares = abs(body.shares)

        if sell_shares > buy_record.remaining_shares:
            return ApiResponse(
                success=False,
                error=f"卖出数量不能超过剩余可卖数量 ({buy_record.remaining_shares})"
            )

        amount = body.price * sell_shares
        fee = max(abs(amount) * body.fee_rate, body.min_fee)
        single_profit = (body.price - float(buy_record.price)) * sell_shares - fee

        trade = Trade(
            buy_order_no=body.buy_order_no,
            contract=buy_record.contract,
            name=buy_record.name,
            price=body.price,
            shares=-sell_shares,
            remaining_shares=0,
            amount=-amount,
            fee=fee,
            net_amount=-(amount + fee),
            trade_type='sell',
            trade_date=trade_date,
            realized_profit=0,
            single_profit=single_profit,
            user_id=body.user_id
        )
        db.add(trade)

        buy_record.remaining_shares -= sell_shares
        buy_record.realized_profit = float(buy_record.realized_profit or 0) + single_profit

        recalculate_position(db, buy_record.contract, body.user_id)
        db.commit()

        return ApiResponse(data={"status": "success", "trade_id": trade.id})


@router.put("/batch")
def batch_replace_trades(body: BatchTradeRequest, db: Session = Depends(get_db)):
    """批量替换交易记录（先删后插，自动重算持仓）"""
    user_id = body.user_id

    contracts = set()
    for t in body.trades:
        contracts.add(t.contract)
        for s in t.sells:
            contracts.add(t.contract)

    # 删除旧数据
    db.query(Trade).filter(Trade.user_id == user_id).delete()
    db.query(Position).filter(Position.user_id == user_id).delete()

    # 插入买入记录
    for t in body.trades:
        amount = t.amount or t.price * abs(t.shares)
        fee = t.fee or 0
        net_amount = t.net_amount or (amount + fee)
        trade_date = date.fromisoformat(t.trade_date) if t.trade_date else date.today()

        buy = Trade(
            buy_order_no=t.buy_order_no,
            contract=t.contract,
            name=t.name,
            price=t.price,
            shares=t.shares,
            remaining_shares=t.remaining_shares,
            amount=amount,
            fee=fee,
            net_amount=net_amount,
            trade_type='buy',
            trade_date=trade_date,
            realized_profit=t.realized_profit or 0,
            single_profit=0,
            user_id=user_id,
        )
        db.add(buy)
        db.flush()

        # 插入卖出记录
        for s in t.sells:
            sell_amount = s.net_amount or -(s.price * abs(s.shares))
            sell_fee = s.fee or 0
            sell_date = date.fromisoformat(s.trade_date) if s.trade_date else date.today()
            sell = Trade(
                buy_order_no=t.buy_order_no,
                contract=t.contract,
                name=t.name,
                price=s.price,
                shares=-abs(s.shares),
                remaining_shares=0,
                amount=sell_amount,
                fee=sell_fee,
                net_amount=sell_amount,
                trade_type='sell',
                trade_date=sell_date,
                realized_profit=0,
                single_profit=s.single_profit or 0,
                user_id=user_id,
            )
            db.add(sell)

    # 重算持仓
    for contract in contracts:
        recalculate_position(db, contract, user_id)

    db.commit()
    return ApiResponse(data={"status": "success", "count": len(body.trades)})


@router.delete("/{trade_id}")
def delete_trade(trade_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """删除交易记录"""
    trade = db.query(Trade).filter(
        Trade.id == trade_id,
        Trade.user_id == user_id
    ).first()

    if not trade:
        return ApiResponse(success=False, error="交易记录不存在")

    contract = trade.contract

    if trade.trade_type == 'buy':
        sell_count = db.query(Trade).filter(
            Trade.buy_order_no == trade.buy_order_no,
            Trade.trade_type == 'sell'
        ).count()

        if sell_count > 0:
            return ApiResponse(
                success=False,
                error=f"该买入记录已有 {sell_count} 笔卖出，不能删除。请先删除所有关联的卖出记录。"
            )

        db.delete(trade)
    else:
        buy_record = db.query(Trade).filter(
            Trade.buy_order_no == trade.buy_order_no,
            Trade.trade_type == 'buy'
        ).first()

        if buy_record:
            sell_shares = abs(trade.shares)
            buy_record.remaining_shares += sell_shares
            buy_record.realized_profit = float(buy_record.realized_profit or 0) - float(trade.single_profit or 0)

        db.delete(trade)

    recalculate_position(db, contract, user_id)
    db.commit()

    return ApiResponse(data={"status": "success"})
