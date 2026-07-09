"""自定义响应类"""
from fastapi.responses import JSONResponse


class CharsetJSONResponse(JSONResponse):
    """带 charset=utf-8 的 JSON 响应"""
    media_type = "application/json; charset=utf-8"
