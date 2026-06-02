from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, text

from app.database import Base


class Position(Base):
    """持仓"""
    __tablename__ = "fnos_positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, nullable=False, default=1)
    total_shares = Column(Integer, nullable=False, default=0)
    avg_cost = Column(DECIMAL(10, 4), default=0)
    latest_price = Column(DECIMAL(10, 4), default=0)
    market_value = Column(DECIMAL(12, 2), default=0)
    profit = Column(DECIMAL(12, 2), default=0)
    profit_rate = Column(DECIMAL(8, 2), default=0)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
