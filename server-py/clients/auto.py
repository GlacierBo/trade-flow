"""自动 Failover 提供商：主选 Sina，失败降级到 EastMoney"""

import logging

from clients.eastmoney import get_stocks as em_get_stocks
from clients.eastmoney import search_stocks as em_search
from clients.sina import get_stocks as sina_get_stocks
from clients.sina import search_stocks as sina_search

logger = logging.getLogger(__name__)


async def get_stocks(codes: list[str]) -> list[dict]:
    """优先 Sina，降级 EastMoney，最终返回兜底数据"""
    if not codes:
        return []

    # 1. 尝试 Sina
    try:
        results = await sina_get_stocks(codes)
        if results and any(s.get("name") and s["name"] != "---" for s in results):
            # 将有效结果按入参顺序排列
            code_map = {s["code"]: s for s in results if s.get("name") and s["name"] != "---"}
            ordered = [code_map.get(c) for c in codes if c in code_map]
            return ordered
    except Exception as e:
        logger.warning("sina get_stocks failed: %s", e)

    # 2. 降级 EastMoney
    try:
        results = await em_get_stocks(codes)
        if results:
            return results
    except Exception as e:
        logger.warning("eastmoney get_stocks failed: %s", e)

    return [{"code": c, "name": "---"} for c in codes]


async def get_stock(code: str) -> dict | None:
    stocks = await get_stocks([code])
    return stocks[0] if stocks else None


async def search_stocks(keyword: str) -> list[dict]:
    """优先 Sina 搜索，降级 EastMoney"""
    # 1. 尝试 Sina
    try:
        results = await sina_search(keyword)
        if results and any(s.get("name") and s["name"] != "---" for s in results):
            return [s for s in results if s.get("name") and s["name"] != "---"]
    except Exception as e:
        logger.warning("sina search failed: %s", e)

    # 2. 降级 EastMoney
    try:
        results = await em_search(keyword)
        if results:
            return results
    except Exception as e:
        logger.warning("eastmoney search failed: %s", e)

    return []
