from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, text

from app.database import Base


class PortfolioItem(Base):
    """持仓比例项目"""
    __tablename__ = "fnos_portfolio_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    contract = Column(String(50), nullable=False)
    tag = Column(String(50), default="")
    price = Column(DECIMAL(18, 2), nullable=False, default=0)
    user_id = Column(Integer, nullable=False, default=1)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
