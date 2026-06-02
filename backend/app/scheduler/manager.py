import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.scheduler.tasks import refresh_watchlist_task

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduler():
    """注册所有定时任务"""
    # 每 10 分钟刷新自选行情
    scheduler.add_job(refresh_watchlist_task, "interval", minutes=10, id="refresh_watchlist")
    logger.info("[scheduler] 注册定时任务: 自选行情每 10 分钟刷新")


async def start_scheduler():
    """启动调度器"""
    from app.scheduler.tasks import refresh_watchlist_task

    # 启动时立即执行一次
    await refresh_watchlist_task()

    setup_scheduler()
    scheduler.start()
    logger.info("[scheduler] 调度器已启动")


def stop_scheduler():
    """停止调度器"""
    scheduler.shutdown(wait=False)
    logger.info("[scheduler] 调度器已停止")
