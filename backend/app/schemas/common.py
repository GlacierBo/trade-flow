"""通用响应对象"""
from typing import Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一 API 响应"""
    success: bool = True
    data: Optional[object] = None
    error: Optional[str] = None
