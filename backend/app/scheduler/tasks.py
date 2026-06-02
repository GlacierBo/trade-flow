import logging

from app.database import SessionLocal

logger = logging.getLogger(__name__)


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
