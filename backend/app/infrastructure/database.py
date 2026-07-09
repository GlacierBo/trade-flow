from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.infrastructure.config import DATABASE_TYPE, DATABASE_URL

# SQLite needs check_same_thread=False for uvicorn's multi-threaded access
engine_kwargs = {"pool_pre_ping": True}
if DATABASE_TYPE == "sqlite":
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
