from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, text

from app.database import Base


class Stock(Base):
    __tablename__ = "fnos_stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(100))
    price = Column(DECIMAL(12, 4))
    changePercent = Column(DECIMAL(12, 4))
    open = Column(DECIMAL(12, 4))
    high = Column(DECIMAL(12, 4))
    low = Column(DECIMAL(12, 4))
    yesterday = Column(DECIMAL(12, 4))
    volume = Column(DECIMAL(20, 4))
    amount = Column(DECIMAL(20, 4))
    amplitude = Column(DECIMAL(12, 4))
    turnoverRate = Column(DECIMAL(12, 4))
    totalMarketCap = Column(DECIMAL(20, 4))
    source = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class Watchlist(Base):
    __tablename__ = "fnos_watchlist"

    code = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    added_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
