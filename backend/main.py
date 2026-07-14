import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.infrastructure.config import PORT
from app.infrastructure.database import Base, engine
from app.interfaces.middleware.exception_handler import global_exception_handler
from app.interfaces.responses import CharsetJSONResponse
from app.interfaces.routers import stocks, watchlist, trades, positions, portfolio, trade_tags, auth, contracts, allocator
from app.infrastructure.scheduler.manager import start_scheduler, stop_scheduler

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


app = FastAPI(
    title="TradeFlow Server",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=CharsetJSONResponse,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
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
app.include_router(allocator.router)

# 静态文件 & SPA 路由
public_dir = os.path.join(os.path.dirname(__file__), "public")
index_file = os.path.join(public_dir, "index.html")

if os.path.isdir(public_dir):
    assets_dir = os.path.join(public_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    _real_public = os.path.realpath(public_dir)

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.realpath(os.path.join(public_dir, full_path))
        if full_path and file_path.startswith(_real_public) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(index_file)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
