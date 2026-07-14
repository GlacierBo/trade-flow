from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, text

from app.infrastructure.database import Base


class AllocatorPosition(Base):
    """分配器持仓"""
    __tablename__ = "fnos_allocator_positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=1)
    variety = Column(String(50), nullable=False, default="")
    contract_code = Column(String(50), nullable=False, default="")
    contract_name = Column(String(100), nullable=False, default="")
    price = Column(DECIMAL(18, 2), nullable=False, default=0)
    amount = Column(DECIMAL(18, 2), nullable=False, default=0)
    color = Column(String(50), nullable=False, default="")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
