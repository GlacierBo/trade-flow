from sqlalchemy import Column, String, TIMESTAMP, text

from app.database import Base


class Watchlist(Base):
    """自选股"""
    __tablename__ = "fnos_watchlist"

    code = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    added_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
