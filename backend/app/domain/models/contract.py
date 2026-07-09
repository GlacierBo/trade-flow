from sqlalchemy import Column, Integer, String, TIMESTAMP, text

from app.infrastructure.database import Base


class Contract(Base):
    """合约管理"""
    __tablename__ = "fnos_contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, nullable=False, default=1)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
