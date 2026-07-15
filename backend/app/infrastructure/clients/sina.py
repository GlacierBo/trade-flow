"""新浪行情 API 提供商"""

import re

import httpx

HEADERS = {
    "Referer": "https://finance.sina.com.cn/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def code_to_sina(code: str) -> str:
    """SH510050 -> sh510050, SZ000001 -> sz000001"""
    if code.startswith("SH"):
        return "sh" + code[2:]
    if code.startswith("SZ"):
        return "sz" + code[2:]
    if code.startswith("HK"):
        return "hk" + code[2:]
    return code.lower()


def to_num(v: str) -> float | None:
    v = v.strip()
    if not v or v == "-" or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def parse_sina_row(row: str) -> dict | None:
    """解析新浪行情数据: var hq_str_sh510050="...";"""
    match = re.match(r'var hq_str_(\w+)="(.+)"', row.strip())
    if not match:
        return None
    code = match.group(1).upper()
    params = match.group(2).split(",")
    if len(params) < 30:
        return None

    name = params[0]
    open_p = to_num(params[1])
    yesterday = to_num(params[2])
    now = to_num(params[3])
    high = to_num(params[4])
    low = to_num(params[5])

    change_percent = None
    if now is not None and yesterday is not None and yesterday != 0:
        change_percent = round((now - yesterday) / yesterday * 100, 2)

    return {
        "code": code,
        "name": name,
        "price": now,
        "changePercent": change_percent,
        "open": open_p,
        "high": high,
        "low": low,
        "yesterday": yesterday,
        "volume": to_num(params[8]) if len(params) > 8 else None,
        "amount": to_num(params[9]) if len(params) > 9 else None,
        "amplitude": None,
        "turnoverRate": None,
        "totalMarketCap": None,
        "source": "sina",
    }


async def get_stocks(codes: list[str]) -> list[dict]:
    if not codes:
        return []
    api_codes = ",".join(code_to_sina(c) for c in codes)
    url = f"https://hq.sinajs.cn/list={api_codes}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=HEADERS)
            text = resp.content.decode("gbk", errors="replace")
    except Exception:
        return []

    results = []
    for line in text.strip().split("\n"):
        parsed = parse_sina_row(line)
        if parsed:
            results.append(parsed)

    code_map = {code_to_sina(c): c for c in codes}
    ordered = []
    for r in results:
        sina_code = r["code"].lower()
        unified = code_map.get(sina_code, r["code"])
        r["code"] = unified
        ordered.append(r)
    return ordered


async def get_stock(code: str) -> dict | None:
    stocks = await get_stocks([code])
    return stocks[0] if stocks else None


async def search_stocks(keyword: str) -> list[dict]:
    """新浪搜索"""
    url = f"http://suggest3.sinajs.cn/suggest/type=2&key={keyword}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=HEADERS)
            text = resp.content.decode("gb18030", errors="replace")
    except Exception:
        return []

    match = re.search(r'var suggestvalue="([^"]*)"', text)
    if not match:
        return []
    items = match.group(1).split(";")
    codes = []
    for item in items:
        if not item.strip():
            continue
        parts = item.split(",")
        raw_code = parts[0] if parts else ""
        if raw_code.startswith("sh"):
            codes.append(f"SH{raw_code[2:]}")
        elif raw_code.startswith("sz"):
            codes.append(f"SZ{raw_code[2:]}")
        elif raw_code.startswith("of"):
            fund_code = raw_code[2:]
            codes.append(f"SH{fund_code}")
            codes.append(f"SZ{fund_code}")

    if not codes:
        return []

    stocks = await get_stocks(codes)
    if stocks:
        seen = set()
        unique = []
        for s in stocks:
            if s["code"] not in seen:
                seen.add(s["code"])
                unique.append(s)
        return unique
    return []
