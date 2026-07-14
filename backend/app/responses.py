"""自定义响应类"""
from starlette.responses import JSONResponse


class CharsetJSONResponse(JSONResponse):
    """显式设置 charset=utf-8 避免中文乱码"""
    media_type = "application/json; charset=utf-8"
