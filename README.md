# TradeFlow

网格交易记录 & 持仓比例分析工具。

追踪每笔网格交易的盈利，管理资产配置。前端 Vue 3 + Tailwind CSS，后端 Supabase（PostgreSQL），无需自建服务。

<p align="center">
  <img src="https://img.shields.io/badge/Vue-3.x-4FC08D?logo=vue.js&logoColor=white" alt="Vue 3" />
  <img src="https://img.shields.io/badge/Vite-5.x-646CFF?logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/Pinia-2.x-DD0031?logo=pinia&logoColor=white" alt="Pinia" />
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white" alt="Supabase" />
  <img src="https://img.shields.io/badge/Tailwind-CSS-06B6D4?logo=tailwindcss&logoColor=white" alt="Tailwind CSS" />
</p>

---

## Features

- **网格交易记录** — 买入/卖出关联记录，自动生成单号，支持分批卖出
- **盈利自动计算** — 每笔卖出自动算收益，累计收益实时更新
- **成本摊薄跟踪** — 网格高抛低吸，持仓成本持续降低，数据一目了然
- **持仓概览** — 持仓数量、成本、现价、浮动盈亏，已平仓记录保留可查
- **快捷交易** — 常用合约一键标签化，快速发起网格操作
- **持仓比例分析** — 按 Tag 分组计算各资产占比，进度条配色，金额显隐切换
- **全量重算机制** — 每次交易变动自动重算持仓和盈亏，数据准确
- **用户认证** — 用户名注册/登录，MD5+盐值加密，管理员可管理用户、重置密码
- **数据隔离** — 多用户独立数据，每个用户只能看到和操作自己的交易、持仓、标签和持仓比例数据
- **股票查询** — 搜索股票代码/名称，实时查看行情（现价、涨跌幅、最高/最低、昨收）
- **自选股管理** — 添加/删除自选股，支持多数据源（东方财富），价格自动刷新

## Tech Stack

| Frontend | Backend | Build |
|----------|---------|-------|
| Vue 3 (Composition API) | Supabase (PostgreSQL) | Vite 5 |
| Pinia 2 | 东方财富行情 API（通过本地代理服务） | Tailwind CSS 3 |
| No router (SPA view switching) | DB Triggers for auto recalc | PostCSS |

## Quick Start

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 Supabase URL 和 Anon Key

# 2. 安装依赖
npm install

# 3. 初始化数据库
# 在 Supabase Dashboard → SQL Editor 依次执行：
#   sql/supabase-schema.sql
#   sql/supabase-schema-tags.sql

# 4. 启动
npm run dev
```

访问 `http://localhost:5173`。

默认账号：
| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin | 管理员 |
| user001 | 123456 | 普通用户 |

## Directory Structure

```
src/
├── App.vue                  # Root: auth guard + tab navigation
├── main.js                  # Entry: mount app, init Pinia
├── style.css                # Tailwind directives + custom animations
├── api/stock.js             # Supabase client + all API functions
├── api/stock-quote.js       # 东方财富行情 API（搜索、实时报价）
├── stores/stock.js          # Pinia store (state, actions, modals)
├── stores/stocks.js         # Pinia store（股票搜索状态）
├── stores/watchlist.js      # Pinia store（自选股、localStorage 持久化、定时刷新）
└── components/
    ├── LoginPage.vue        # Login / Register (username + auto-generated password)
    ├── TradeList.vue        # Trade history (buys with sell children)
    ├── TradeModal.vue       # Add/edit trade dialog
    ├── SellModal.vue        # Sell against a buy order
    ├── PositionList.vue     # Position overview (active + closed)
    ├── QuickTrade.vue       # Quick-trade tag list
    ├── ConfirmModal.vue     # Confirmation dialog
    ├── Toast.vue            # Toast notifications
    ├── PortfolioRatio.vue   # Portfolio ratio calculator page
    ├── PortfolioModal.vue   # Add portfolio item dialog
    ├── UserManagement.vue   # Admin: paginated user list, reset passwords
    ├── ChangePasswordForm.vue # Change password modal
    ├── StockSearch.vue      # 股票搜索主页面（搜索框 + 自选面板 + 结果网格）
    ├── SearchBar.vue        # 搜索输入框（防抖自动搜索）
    ├── StockGrid.vue        # 搜索结果网格布局
    ├── StockCard.vue        # 股票卡片（名称、代码、现价、涨跌幅）
    ├── StockDetailModal.vue # 股票详情弹窗
    └── WatchlistPanel.vue   # 自选股面板（涨跌幅、删除、定时刷新）
sql/
├── supabase-schema.sql      # Core schema: trades, positions, counters, triggers
└── supabase-schema-tags.sql # Tags, portfolio_items, app_users + auth RPC functions
```

## Database

PostgreSQL tables managed via Supabase. Key design:

- **`stock_trades`** — All buy/sell records linked by `buy_order_no`, isolated by `user_id`
- **`stock_positions`** — Auto-calculated view per user per contract, recalculated by DB trigger on every trade change
- **`stock_trade_tags`** — Quick-trade presets, auto-created on buy, isolated by `user_id`
- **`portfolio_items`** — Portfolio ratio data source (name, contract, tag, price), isolated by `user_id`. Same contract auto-accumulates price instead of duplicate rows.
- **`app_users`** — User accounts with MD5+salt password hashing, role-based access (user/admin)

All business tables use `user_id` for multi-tenant data isolation — each user only sees their own data.

## Deployment

Push to GitHub. GitHub Actions builds and deploys to GitHub Pages automatically.

1. 在仓库 Settings → Actions secrets 添加 `VITE_SUPABASE_URL` 和 `VITE_SUPABASE_ANON_KEY`
2. 推送 main 分支即可
