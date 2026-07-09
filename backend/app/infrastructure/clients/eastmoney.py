"""东方财富行情 API 提供商"""

import httpx

QUERY_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get"
SUGGEST_URL = "https://searchapi.eastmoney.com/api/suggest/get"
SUGGEST_TOKEN = "D43BF722C8E33BDC906FB84D85E326E8"
FIELDS = ",".join([
    "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f10",
    "f12", "f14", "f15", "f16", "f17", "f18", "f20", "f21", "f69",
])
HEADERS = {
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://quote.eastmoney.com/",
    "User-Agent": "Mozilla/5.0 (compatible; stock-api/2.0)",
}


def code_to_secid(code: str) -> str:
    if code.startswith("SH"):
        return f"1.{code[2:]}"
    if code.startswith("SZ"):
        return f"0.{code[2:]}"
    return code


def to_num(v) -> float | None:
    if v is None or v == "-":
        return None
    try:
        n = float(v)
        return n
    except (ValueError, TypeError):
        return None


def parse_quote(q: dict) -> dict:
    return {
        "code": q.get("f12", ""),
        "name": q.get("f14", "---"),
        "price": to_num(q.get("f2")),
        "changePercent": to_num(q.get("f3")),
        "open": to_num(q.get("f17")),
        "high": to_num(q.get("f15")),
        "low": to_num(q.get("f16")),
        "yesterday": to_num(q.get("f18")),
        "volume": to_num(q.get("f5")),
        "amount": to_num(q.get("f6")),
        "amplitude": to_num(q.get("f7")),
        "turnoverRate": to_num(q.get("f8")),
        "totalMarketCap": to_num(q.get("f20")),
        "source": "eastmoney",
    }


async def get_stocks(codes: list[str]) -> list[dict]:
    if not codes:
        return []
    secids = ",".join(code_to_secid(c) for c in codes)
    url = f"{QUERY_URL}?fltt=2&secids={secids}&fields={FIELDS}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=HEADERS, timeout=15)
            data = resp.json()
    except Exception:
        return []

    diff = data.get("data", {}).get("diff")
    if not diff:
        return []
    quotes = diff if isinstance(diff, list) else list(diff.values())

    code_map = {}
    for c in codes:
        if not c:
            continue
        raw = c[2:] if c.startswith(("SH", "SZ")) else c
        code_map[raw] = c

    results = []
    for q in quotes:
        if not q.get("f12"):
            continue
        raw_code = str(q["f12"])
        unified_code = code_map.get(raw_code, raw_code)
        result = parse_quote(q)
        result["code"] = unified_code
        results.append(result)
    return results


async def get_stock(code: str) -> dict | None:
    stocks = await get_stocks([code])
    return stocks[0] if stocks else None


async def search_stocks(keyword: str) -> list[dict]:
    url = f"{SUGGEST_URL}?input={keyword}&type=14&token={SUGGEST_TOKEN}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=HEADERS, timeout=15)
            data = resp.json()
    except Exception:
        return []

    items = (data.get("QuotationCodeTable") or {}).get("Data") or []
    codes = []
    suggest_map = {}
    for item in items:
        code = item.get("Code") or ""
        name = item.get("Name") or ""
        market = str(item.get("MktNum") or "")
        if not code:
            continue
        if market == "1":
            unified = f"SH{code}"
        elif market == "0":
            unified = f"SZ{code}"
        else:
            continue
        codes.append(unified)
        suggest_map[unified] = {"code": unified, "name": name, "source": "eastmoney"}

    if not codes:
        return []

    stocks = await get_stocks(codes)
    if stocks:
        return stocks

    return list(suggest_map.values())
