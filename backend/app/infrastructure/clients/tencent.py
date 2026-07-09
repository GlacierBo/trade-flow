"""腾讯股票行情 API 客户端"""

import logging
import re
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)

# 腾讯行情 API
QUOTE_URL = "https://qt.gtimg.cn/q={codes}"
SEARCH_URL = "https://smartbox.gtimg.cn/s3/?v=2&t=all&c=1&q={keyword}"


def _convert_code(code: str) -> str:
    """将内部代码转换为腾讯 API 代码
    SH510500 -> sh510500
    SZ159915 -> sz159915
    """
    if not code:
        return ""
    code = code.upper()
    if code.startswith("SH"):
        return "sh" + code[2:]
    elif code.startswith("SZ"):
        return "sz" + code[2:]
    return code.lower()


def _parse_internal_code(tencent_code: str) -> str:
    """将腾讯代码转换为内部代码
    sh510500 -> SH510500
    sz159915 -> SZ159915
    """
    if not tencent_code:
        return ""
    tencent_code = tencent_code.lower()
    if tencent_code.startswith("sh"):
        return "SH" + tencent_code[2:]
    elif tencent_code.startswith("sz"):
        return "SZ" + tencent_code[2:]
    return tencent_code.upper()


def _parse_quote_line(line: str) -> dict | None:
    """解析腾讯行情数据行"""
    try:
        match = re.match(r'v_(\w+)="(.+)"', line)
        if not match:
            return None

        api_code = match.group(1)
        data = match.group(2)
        fields = data.split("~")

        if len(fields) < 50:
            return None

        code = _parse_internal_code(api_code)
        name = fields[1]
        price = float(fields[3]) if fields[3] else 0
        yesterday = float(fields[4]) if fields[4] else 0
        open_price = float(fields[5]) if fields[5] else 0

        change_percent = 0
        if yesterday > 0 and price > 0:
            change_percent = ((price - yesterday) / yesterday) * 100

        return {
            "code": code,
            "name": name,
            "price": price,
            "changePercent": round(change_percent, 2),
            "open": open_price,
            "high": float(fields[33]) if fields[33] and len(fields) > 33 else 0,
            "low": float(fields[34]) if fields[34] and len(fields) > 34 else 0,
            "yesterday": yesterday,
            "volume": float(fields[6]) if fields[6] else 0,
            "amount": float(fields[37]) if fields[37] and len(fields) > 37 else 0,
            "amplitude": 0,
            "turnoverRate": float(fields[38]) if fields[38] and len(fields) > 38 else 0,
            "totalMarketCap": float(fields[45]) if fields[45] and len(fields) > 45 else 0,
            "source": "tencent",
        }
    except Exception as e:
        logger.warning("解析腾讯行情数据失败: %s, line: %s", e, line[:100])
        return None


async def get_stocks(codes: list[str]) -> list[dict]:
    """批量查询股票行情"""
    if not codes:
        return []

    api_codes = [_convert_code(c) for c in codes]
    api_codes = [c for c in api_codes if c]

    if not api_codes:
        return []

    url = QUOTE_URL.format(codes=",".join(api_codes))

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            text = response.content.decode("gbk", errors="ignore")

            results = []
            for line in text.strip().split("\n"):
                stock = _parse_quote_line(line.strip())
                if stock and stock.get("name") and stock["name"] != "---":
                    results.append(stock)

            return results
    except Exception as e:
        logger.error("腾讯行情查询失败: %s", e)
        return []


async def search_stocks(keyword: str) -> list[dict]:
    """搜索股票"""
    if not keyword.strip():
        return []

    url = SEARCH_URL.format(keyword=quote(keyword))

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            text = response.content.decode("gbk", errors="ignore")

            match = re.match(r'v_hint="(.+)"', text)
            if not match:
                return []

            rows = match.group(1).split("^")
            results = []

            for row in rows:
                if not row:
                    continue
                parts = row.split("~")
                if len(parts) < 4:
                    continue

                market = parts[0]
                code = parts[1]
                name = parts[2]

                if market in ("sh", "sz"):
                    internal_code = _parse_internal_code(market + code)
                    results.append({
                        "code": internal_code,
                        "name": name,
                        "source": "tencent",
                    })

            return results
    except Exception as e:
        logger.error("腾讯股票搜索失败: %s", e)
        return []
