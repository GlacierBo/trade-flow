import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import PORT
from app.database import Base, engine
from app.middleware.exception_handler import global_exception_handler
from app.routers import stocks, watchlist, trades, positions, portfolio, trade_tags, auth, contracts
from app.scheduler.manager import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时建表
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.warning("数据库连接失败，请检查 MySQL 是否已启动: %s", e)

    # 启动定时任务
    await start_scheduler()

    yield

    stop_scheduler()


app = FastAPI(title="TradeFlow Server", version="1.0.0", lifespan=lifespan)

# 全局异常处理
app.add_exception_handler(Exception, global_exception_handler)

# 注册路由
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
