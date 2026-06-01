# TradeFlow Server

独立部署的股票行情代理服务。提供股票查询、自选股管理，数据持久化到 Supabase（PostgreSQL）。

## 架构

```
浏览器 → http://localhost:3001
            ├── /api/stocks/*   → 东方财富行情 API（实时查询，结果存库）
            ├── /api/watchlist/* → 自选股 CRUD（Supabase 持久化）
            └── /               → 自含的股票搜索+自选管理前端页面
```

## 快速启动

```bash
# 1. 进入 server 目录
cd server

# 2. 配置 Supabase（从 Supabase Dashboard → API 获取）
cp .env.example .env
# 编辑 .env，填入你的 SUPABASE_URL 和 SUPABASE_KEY（建议用 service_role key）

# 3. 安装依赖
npm install

# 4. 在 Supabase SQL Editor 执行建表语句（见下方）

# 5. 启动服务（默认端口 3001）
npm start
```

打开 `http://localhost:3001` 即可使用。

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stocks/search?q=关键词` | 搜索股票（名称/代码）|
| GET | `/api/stocks/:code` | 查询单只股票行情 |
| POST | `/api/stocks/batch` | 批量查询，body: `{ codes: ["SH510500"] }` |
| GET | `/api/watchlist` | 获取自选列表（含最新行情） |
| POST | `/api/watchlist` | 添加自选，body: `{ code, name }` |
| DELETE | `/api/watchlist/:code` | 删除自选 |
| POST | `/api/watchlist/refresh` | 刷新所有自选行情 |

## 数据字段

每条股票数据包含 14 个字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| code | 统一代码 | SH510500 |
| name | 股票名称 | 中证500ETF南方 |
| price | 现价 | 8.512 |
| changePercent | 涨跌幅(%) | 0.82 |
| open | 今开 | 8.434 |
| high | 最高 | 8.513 |
| low | 最低 | 8.393 |
| yesterday | 昨收 | 8.443 |
| volume | 成交量(手) | 1600203 |
| amount | 成交额(元) | 1350227807 |
| amplitude | 振幅(%) | 1.42 |
| turnoverRate | 换手率(%) | 3.69 |
| totalMarketCap | 总市值(元) | 36899252519 |
| source | 数据源 | eastmoney |

建表 SQL 见 [schema.sql](schema.sql)。

## 配合 TradeFlow 前端使用

在 trade-flow 中，「股票查询」页面会调用本服务的 API 展示自选股。

确保本服务先启动（端口 3001），trade-flow 的 Vite 开发服务器会通过 `/api/*` 代理到本服务。

## 技术栈

- Node.js + Express 5
- Supabase（PostgreSQL）
- 数据源：东方财富行情 API
