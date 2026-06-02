from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, text

from app.database import Base


class Stock(Base):
    """股票历史行情"""
    __tablename__ = "fnos_stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(100))
    price = Column(DECIMAL(18, 2))
    changePercent = Column(DECIMAL(18, 2))
    open = Column(DECIMAL(18, 2))
    high = Column(DECIMAL(18, 2))
    low = Column(DECIMAL(18, 2))
    yesterday = Column(DECIMAL(18, 2))
    volume = Column(DECIMAL)
    amount = Column(DECIMAL)
    amplitude = Column(DECIMAL(18, 2))
    turnoverRate = Column(DECIMAL(18, 2))
    totalMarketCap = Column(DECIMAL(18, 2))
    source = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
