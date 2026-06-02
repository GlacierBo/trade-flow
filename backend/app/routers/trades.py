import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Trade, Position, SerialCounter
from app.schemas import ApiResponse, CreateTradeRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trades", tags=["trades"])


def generate_buy_order_no(db: Session, trade_date: date) -> str:
    """生成买入单号：NO + YYYYMMDD + 4位流水号"""
    date_str = trade_date.strftime("%Y%m%d")

    counter = db.query(SerialCounter).filter(
        SerialCounter.counter_date == date_str
    ).with_for_update().first()

    if counter:
        counter.current_serial += 1
        serial = counter.current_serial
    else:
        serial = 1
        db.add(SerialCounter(counter_date=date_str, current_serial=serial))

    db.flush()
    return f"NO{date_str}{serial:04d}"


def recalculate_position(db: Session, contract: str, user_id: int):
    """重新计算持仓"""
    trade = db.query(Trade).filter(
        Trade.contract == contract,
        Trade.user_id == user_id
    ).first()

    if not trade:
        db.query(Position).filter(
            Position.contract == contract,
            Position.user_id == user_id
        ).delete()
        return

    name = trade.name

    buy_stats = db.query(
        func.coalesce(func.sum(Trade.shares), 0),
        func.coalesce(func.sum(Trade.amount), 0)
    ).filter(
        Trade.contract == contract,
        Trade.trade_type == 'buy',
        Trade.user_id == user_id
    ).first()

    total_buy_shares = buy_stats[0]
    total_buy_amount = float(buy_stats[1])

    sell_stats = db.query(
        func.coalesce(func.sum(func.abs(Trade.shares)), 0),
        func.coalesce(func.sum(func.abs(Trade.amount)), 0)
    ).filter(
        Trade.contract == contract,
        Trade.trade_type == 'sell',
        Trade.user_id == user_id
    ).first()

    total_sell_shares = sell_stats[0]
    total_sell_amount = float(sell_stats[1])

    position_shares = total_buy_shares - total_sell_shares

    total_profit = db.query(
        func.coalesce(func.sum(Trade.single_profit), 0)
    ).filter(
        Trade.contract == contract,
        Trade.trade_type == 'sell',
        Trade.user_id == user_id
    ).scalar()

    total_profit = float(total_profit)

    position = db.query(Position).filter(
        Position.contract == contract,
        Position.user_id == user_id
    ).first()

    if position_shares <= 0:
        if position:
            position.total_shares = 0
            position.avg_cost = 0
            position.latest_price = 0
            position.market_value = 0
            position.profit = total_profit
            position.profit_rate = 0
        else:
            db.add(Position(
                contract=contract,
                name=name,
                user_id=user_id,
                total_shares=0,
                avg_cost=0,
                latest_price=0,
                market_value=0,
                profit=total_profit,
                profit_rate=0
            ))
        return

    net_cost = total_buy_amount - total_sell_amount
    avg_cost = net_cost / position_shares

    latest_trade = db.query(Trade).filter(
        Trade.contract == contract,
        Trade.user_id == user_id
    ).order_by(Trade.created_at.desc()).first()

    latest_price = float(latest_trade.price) if latest_trade else 0
    market_value = position_shares * latest_price

    unrealized_profit = (latest_price - avg_cost) * position_shares
    profit_rate = (unrealized_profit / net_cost * 100) if net_cost > 0 else 0

    if position:
        position.name = name
        position.total_shares = position_shares
        position.avg_cost = avg_cost
        position.latest_price = latest_price
        position.market_value = market_value
        position.profit = total_profit
        position.profit_rate = profit_rate
    else:
        db.add(Position(
            contract=contract,
            name=name,
            user_id=user_id,
            total_shares=position_shares,
            avg_cost=avg_cost,
            latest_price=latest_price,
            market_value=market_value,
            profit=total_profit,
            profit_rate=profit_rate
        ))


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
            raise HTTPException(status_code=400, detail="卖出操作必须提供买入单号")

        buy_record = db.query(Trade).filter(
            Trade.buy_order_no == body.buy_order_no,
            Trade.trade_type == 'buy',
            Trade.user_id == body.user_id
        ).first()

        if not buy_record:
            raise HTTPException(status_code=400, detail="找不到对应的买入记录")

        sell_shares = abs(body.shares)

        if sell_shares > buy_record.remaining_shares:
            raise HTTPException(
                status_code=400,
                detail=f"卖出数量不能超过剩余可卖数量 ({buy_record.remaining_shares})"
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
        buy_record.realized_profit += single_profit

        recalculate_position(db, buy_record.contract, body.user_id)
        db.commit()

        return ApiResponse(data={"status": "success", "trade_id": trade.id})


@router.delete("/{trade_id}")
def delete_trade(trade_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """删除交易记录"""
    trade = db.query(Trade).filter(
        Trade.id == trade_id,
        Trade.user_id == user_id
    ).first()

    if not trade:
        raise HTTPException(status_code=404, detail="交易记录不存在")

    contract = trade.contract

    if trade.trade_type == 'buy':
        sell_count = db.query(Trade).filter(
            Trade.buy_order_no == trade.buy_order_no,
            Trade.trade_type == 'sell'
        ).count()

        if sell_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"该买入记录已有 {sell_count} 笔卖出，不能删除。请先删除所有关联的卖出记录。"
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
            buy_record.realized_profit -= trade.single_profit

        db.delete(trade)

    recalculate_position(db, contract, user_id)
    db.commit()

    return ApiResponse(data={"status": "success"})
