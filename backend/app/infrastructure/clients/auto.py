"""自动故障转移客户端"""
import logging

from app.infrastructure.clients.sina import get_stocks as sina_get, search_stocks as sina_search
from app.infrastructure.clients.tencent import get_stocks as tencent_get, search_stocks as tencent_search
from app.infrastructure.clients.eastmoney import get_stocks as em_get, search_stocks as em_search

logger = logging.getLogger(__name__)


async def get_stocks(codes: list[str]) -> list[dict]:
    """批量获取行情，故障转移链：Sina → Tencent → EastMoney"""
    result = await sina_get(codes)
    if _has_valid_data(result):
        return result

    result = await tencent_get(codes)
    if _has_valid_data(result):
        return result

    result = await em_get(codes)
    if _has_valid_data(result):
        return result

    # Give up — return placeholder data so we don't break the UI
    return [{"code": code, "name": "---"} for code in codes]


async def get_stock(code: str) -> dict | None:
    """查单只股票"""
    stocks = await get_stocks([code])
    return stocks[0] if stocks else None


async def search_stocks(keyword: str) -> list:
    """搜索股票，故障转移链：Sina → Tencent → EastMoney"""
    result = await sina_search(keyword)
    if result:
        return result
    result = await tencent_search(keyword)
    if result:
        return result
    return await em_search(keyword)


def _has_valid_data(stocks: list[dict]) -> bool:
    """检查列表中有至少一个有效股票名称"""
    return bool(stocks) and any(
        s.get("name") and s["name"] != "---" for s in stocks
    )
