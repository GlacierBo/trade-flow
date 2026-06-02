from sqlalchemy import Column, Integer, String

from app.database import Base


class SerialCounter(Base):
    """流水号计数器"""
    __tablename__ = "fnos_serial_counters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    counter_date = Column(String(8), nullable=False, unique=True)
    current_serial = Column(Integer, nullable=False, default=0)
