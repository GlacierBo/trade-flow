"""交易服务 —— 订单号生成、持仓重算"""

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.models import Trade, Position, SerialCounter


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
    """根据交易记录重新计算指定合约的持仓"""
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
