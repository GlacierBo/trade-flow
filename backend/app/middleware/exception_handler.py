import logging

from fastapi import Request
from app.responses import CharsetJSONResponse

from app.schemas import ApiResponse

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error("Unhandled error: %s %s - %s", request.method, request.url.path, exc, exc_info=True)
    return CharsetJSONResponse(
        status_code=500,
        content=ApiResponse(success=False, error="服务器内部错误").model_dump(),
    )
