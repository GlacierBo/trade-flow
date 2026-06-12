from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, text, func

from app.database import Base


class TradeTag(Base):
    """交易标签"""
    __tablename__ = "fnos_trade_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    latest_price = Column(DECIMAL(18, 2), default=0)
    user_id = Column(Integer, nullable=False, default=1)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), onupdate=func.now())
