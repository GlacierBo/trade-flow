import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import PORT
from app.database import Base, engine
from app.middleware.exception_handler import global_exception_handler
from app.responses import CharsetJSONResponse
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


app = FastAPI(
    title="TradeFlow Server",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=CharsetJSONResponse,
)

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

# 静态文件 & SPA 路由
public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
index_file = os.path.join(public_dir, "index.html")

if os.path.isdir(public_dir):
    # 挂载构建产物中的静态资源（JS、CSS、图片等）
    assets_dir = os.path.join(public_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # SPA catch-all：所有非 API、非静态文件的路由都返回 index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # 尝试直接返回 public 目录下的文件（如 favicon.ico）
        file_path = os.path.join(public_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # 其余全部返回 index.html，由前端路由接管
        return FileResponse(index_file)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
