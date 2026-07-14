# 外部行情接口对接文档

## 概述

系统接入三个股票行情数据源：**新浪 (Sina)**、**腾讯 (Tencent)**、**东方财富 (EastMoney)**，并实现自动故障转移链。所有客户端位于 `backend/app/infrastructure/clients/`，通过 `auto.py` 统一编排调用顺序。

### 架构

```
客户端请求
    ↓
market service (application/services/market.py)
    ↓
auto.py (故障转移调度)
    ├── sina.py   → hq.sinajs.cn (行情) / suggest3.sinajs.cn (搜索)
    ├── tencent.py → qt.gtimg.cn (行情) / smartbox.gtimg.cn (搜索)
    └── eastmoney.py → push2.eastmoney.com (行情) / searchapi.eastmoney.com (搜索)
```

### 故障转移规则

- **行情查询** (`get_stocks`): Sina → Tencent → EastMoney，任一数据源返回有效数据即停止
- **股票搜索** (`search_stocks`): Sina → Tencent → EastMoney，任一返回非空结果即停止
- 有效数据判断：返回列表中至少有一个股票的 `name` 不为空且不为 `"---"`

---

## 数据结构

### 统一响应字段

所有数据源最终统一输出以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | string | 统一格式代码：`SH`/`SZ` 前缀（如 `SH510050`, `SZ000001`）|
| `name` | string | 股票/基金名称 |
| `price` | float\|null | 当前价 |
| `changePercent` | float\|null | 涨跌幅（百分比，如 1.23 表示涨 1.23%）|
| `open` | float\|null | 今日开盘价 |
| `high` | float\|null | 今日最高价 |
| `low` | float\|null | 今日最低价 |
| `yesterday` | float\|null | 昨收价 |
| `volume` | float\|null | 成交量（股） |
| `amount` | float\|null | 成交额（元） |
| `amplitude` | float\|null | 振幅（百分比）|
| `turnoverRate` | float\|null | 换手率（百分比）|
| `totalMarketCap` | float\|null | 总市值（元）|
| `source` | string | 数据源标识：`sina`/`tencent`/`eastmoney` |

---

## 各数据源详情

### 1. 新浪 (Sina)

| 项目 | 内容 |
|------|------|
| 文件 | `clients/sina.py` |
| 代码转换 | `SH510050` → `sh510050` |

#### 行情接口 `get_stocks(codes)`

- **URL**: `https://hq.sinajs.cn/list={codes}`
- **方法**: GET
- **参数**: `codes` — 逗号分隔，格式 `sh510050,sz000001`
- **请求头**: 需携带 `Referer: https://finance.sina.com.cn/`
- **响应格式**: JavaScript 变量赋值文本

```ini
var hq_str_sh510050="华夏上证50ETF,2.803,2.803,2.800,2.809,2.797,...";
var hq_str_sz000001="平安银行,11.25,11.26,11.20,11.30,11.18,...";
```

- **解析**: 通过正则 `var hq_str_(\w+)="(.+)"` 提取，字段以逗号分隔

| 位置 | 字段 | 说明 |
|------|------|------|
| 0 | name | 名称 |
| 1 | open | 开盘价 |
| 2 | yesterday | 昨收价 |
| 3 | now | 当前价 → `price` |
| 4 | high | 最高价 |
| 5 | low | 最低价 |
| 8 | volume | 成交量 |
| 9 | amount | 成交额 |

- `changePercent` = `(now - yesterday) / yesterday * 100`（自行计算）

#### 搜索接口 `search_stocks(keyword)`

- **URL**: `http://suggest3.sinajs.cn/suggest/type=2&key={keyword}`
- **响应格式**: JavaScript 赋值文本

```ini
var suggestvalue="sh,510050,华夏上证50ETF,100,1;sz,000001,平安银行,200,1";
```

- **解析**: 提取 `suggestvalue` 内容，按 `;` 拆分，每项按 `,` 拆分，取第 0 位为原始代码（含 sh/sz 前缀）
- **注意**: 新浪搜索仅返回代码和名称搜索到后，会**再次调用 `get_stocks`** 获取完整行情数据再返回。若行情查询失败，搜索返回空列表

---

### 2. 腾讯 (Tencent)

| 项目 | 内容 |
|------|------|
| 文件 | `clients/tencent.py` |
| 代码转换 | `SH510050` → `sh510050` |

#### 行情接口 `get_stocks(codes)`

- **URL**: `https://qt.gtimg.cn/q={codes}`
- **方法**: GET
- **参数**: `codes` — 逗号分隔，格式 `sh510050,sz000001`
- **响应格式**: JavaScript 变量赋值文本（GBK 编码）

```ini
v_sh510050="1~华夏上证50ETF~2.800~2.803~2.803~2.809~2.797...";
v_sz000001="1~平安银行~11.20~11.25~11.26~11.30~11.18...";
```

- **解析**: 通过正则 `v_(\w+)="(.+)"` 提取，字段以 `~` 分隔

| 位置 | 字段 | 说明 |
|------|------|------|
| 1 | name | 名称 |
| 3 | price | 当前价 |
| 4 | yesterday | 昨收价 |
| 5 | open | 开盘价 |
| 6 | volume | 成交量 |
| 33 | high | 最高价 |
| 34 | low | 最低价 |
| 37 | amount | 成交额 |
| 38 | turnoverRate | 换手率 |
| 45 | totalMarketCap | 总市值 |

- `changePercent` = `(price - yesterday) / yesterday * 100`（自行计算）

#### 搜索接口 `search_stocks(keyword)`

- **URL**: `https://smartbox.gtimg.cn/s3/?v=2&t=all&c=1&q={keyword}`
- **响应格式**: JavaScript 变量赋值文本

```ini
v_hint="sh~510050~华夏上证50ETF~1.00^sz~000001~平安银行~1.00";
```

- **解析**: 提取 `v_hint` 内容，按 `^` 拆分，每项按 `~` 拆分，取 market(0), code(1), name(2)
- **注意**: 腾讯搜索**只返回 `{code, name, source}`，不包含行情数据**。搜索结果显示时前端不会立即有价格

---

### 3. 东方财富 (EastMoney)

| 项目 | 内容 |
|------|------|
| 文件 | `clients/eastmoney.py` |
| 代码转换 | `SH510050` → 平台代码 `1.510050`（数字部分） |

#### 行情接口 `get_stocks(codes)`

- **URL**: `https://push2.eastmoney.com/api/qt/ulist.np/get`
- **方法**: GET
- **query 参数**:

| 参数 | 说明 |
|------|------|
| `fltt` | 浮点数精度，固定 `2` |
| `secids` | 证券 ID，逗号分隔，格式 `1.510050,0.000001`（SH→1, SZ→0 + 纯数字代码）|
| `fields` | 请求字段列表，逗号分隔 |

- **请求字段 (FIELDS)**:

```
f2,f3,f4,f5,f6,f7,f8,f10,f12,f14,f15,f16,f17,f18,f20,f21,f69
```

- **响应格式**: JSON

```json
{
  "data": {
    "diff": [
      {"f12": "510050", "f14": "华夏上证50ETF", "f2": 2.800, ...}
    ]
  }
}
```

- **字段映射**:

| API 字段 | 内部字段 | 说明 |
|----------|----------|------|
| f12 | code | 股票代码（纯数字） |
| f14 | name | 名称 |
| f2 | price | 当前价 |
| f3 | changePercent | 涨跌幅 |
| f15 | high | 最高价 |
| f16 | low | 最低价 |
| f17 | open | 开盘价 |
| f18 | yesterday | 昨收价 |
| f5 | volume | 成交量 |
| f6 | amount | 成交额 |
| f7 | amplitude | 振幅 |
| f8 | turnoverRate | 换手率 |
| f20 | totalMarketCap | 总市值 |

#### 搜索接口 `search_stocks(keyword)`

- **URL**: `https://searchapi.eastmoney.com/api/suggest/get`
- **方法**: GET
- **query 参数**:

| 参数 | 说明 |
|------|------|
| `input` | 搜索关键字 |
| `type` | 固定 `14` |
| `token` | 固定值 `D43BF722C8E33BDC906FB84D85E326E8` |

- **响应格式**: JSON

```json
{
  "QuotationCodeTable": {
    "Data": [
      {"Code": "510050", "Name": "华夏上证50ETF", "MktNum": "1"},
      {"Code": "000001", "Name": "平安银行", "MktNum": "0"}
    ]
  }
}
```

- **市场标识**: `MktNum=1` → SH 前缀, `MktNum=0` → SZ 前缀
- **解析后**: 获取代码列表后，**再次调用 `get_stocks`** 获取完整行情数据返回
- **降级处理**: 若 `get_stocks` 失败，返回仅含 `{code, name, source}` 的基础信息

---

## 服务层调用入口

`backend/app/application/services/market.py` 对外暴露三个方法：

```python
async def search_stocks(keyword: str, source: str = "auto") -> list[dict]
async def get_stock(code: str, db: Session) -> dict | None
async def get_stocks(codes: list[str]) -> list[dict]
```

- `source` 参数支持 `"auto"`（默认故障转移）、`"sina"`、`"tencent"`、`"eastmoney"`
- `get_stock` 优先查询本地数据库 (`stocks` 表），DB 未命中时调用第三方 API 并自动入库缓存

## HTTP 接口暴露

所有行情接口通过 FastAPI 暴露给前端（`routers/stocks.py`）：

| 端点 | 方法 | 说明 | 前端 API 函数 |
|------|------|------|-------------|
| `/api/stocks/search?q=&source=` | GET | 搜索股票 | `searchStocks(keyword, source)` |
| `/api/stocks/{code}` | GET | 查询单只股票 | `getStock(code)` |
| `/api/stocks/batch` | POST | 批量查询行情 | `getStocksBatch(codes)` |

## 注意事项

1. **编码问题**: 新浪返回 GB18030 编码，腾讯返回 GBK 编码，需 `decode()` 处理。东方财富为 UTF-8 JSON
2. **请求头**: 新浪接口需携带 `Referer` 头，否则可能被拦截
3. **超时设置**: 所有客户端统一使用 10-15 秒超时
4. **并发限制**: 当前未做并发限制，如需大规模查询建议添加限流
5. **数据一致性**: 不同数据源同一时刻的行情价格可能存在细微差异，属正常现象
6. **搜索结果的行情**: 东方财富搜索成功时会附带回行情数据；腾讯搜索仅返回基础信息（代码+名称），如需价格需单独调用 `/api/stocks/batch` 接口查询
