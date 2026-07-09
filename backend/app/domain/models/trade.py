from sqlalchemy import Column, Integer, String, DECIMAL, Date, TIMESTAMP, text

from app.infrastructure.database import Base


class Trade(Base):
    """交易记录"""
    __tablename__ = "fnos_trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    buy_order_no = Column(String(20))
    contract = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 4), nullable=False)
    shares = Column(Integer, nullable=False)
    remaining_shares = Column(Integer, default=0)
    amount = Column(DECIMAL(12, 2), nullable=False)
    fee = Column(DECIMAL(10, 2), nullable=False, default=0)
    net_amount = Column(DECIMAL(12, 2), nullable=False)
    trade_type = Column(String(10), nullable=False)
    trade_date = Column(Date, nullable=False)
    user_id = Column(Integer, nullable=False, default=1)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    realized_profit = Column(DECIMAL(12, 2), default=0)
    single_profit = Column(DECIMAL(12, 2), default=0)
