import asyncio
import logging
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import PORT
from app.database import Base, SessionLocal, engine
from app.routers import stocks, watchlist, trades, positions, portfolio, trade_tags, auth, contracts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def refresh_watchlist_task():
    """定时刷新所有自选行情"""
    try:
        db = SessionLocal()
        try:
            from app.services.watchlist import refresh_watchlist as ref

            await ref(db)
            logger.info("[scheduler] 自选行情已刷新")
        finally:
            db.close()
    except Exception as e:
        logger.error("[scheduler] 刷新失败: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时建表
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.warning("数据库连接失败，请检查 MySQL 是否已启动: %s", e)

    # 启动时立即刷新一次
    await refresh_watchlist_task()

    # 每 10 分钟定时刷新
    scheduler.add_job(refresh_watchlist_task, "interval", minutes=10)
    scheduler.start()
    logger.info("[scheduler] 自选行情每 10 分钟自动刷新")

    yield

    scheduler.shutdown(wait=False)


app = FastAPI(title="TradeFlow Server", version="1.0.0", lifespan=lifespan)

app.include_router(stocks.router)
app.include_router(watchlist.router)
app.include_router(trades.router)
app.include_router(positions.router)
app.include_router(portfolio.router)
app.include_router(trade_tags.router)
app.include_router(auth.router)
app.include_router(contracts.router)

# 静态文件
public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.isdir(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
