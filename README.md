# TradeFlow

网格交易记录 & 持仓比例分析工具。

追踪每笔网格交易的盈利，管理资产配置。前端 Vue 3 + Tailwind CSS，后端 Python FastAPI + MySQL。

<p align="center">
  <img src="https://img.shields.io/badge/Vue-3.x-4FC08D?logo=vue.js&logoColor=white" alt="Vue 3" />
  <img src="https://img.shields.io/badge/Vite-5.x-646CFF?logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/Pinia-2.x-DD0031?logo=pinia&logoColor=white" alt="Pinia" />
  <img src="https://img.shields.io/badge/FastAPI-Python-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/MySQL-8.x-4479A1?logo=mysql&logoColor=white" alt="MySQL" />
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
| Vue 3 (Composition API) | Python FastAPI | Vite 5 |
| Pinia 2 | MySQL | Tailwind CSS 3 |
| Vue Router 4 | 东方财富行情 API | PostCSS |

## Quick Start

### 后端服务

```bash
# 1. 进入后端目录
cd backend

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 MySQL 连接信息

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
# 执行 backend/sql/schema.sql 建表

# 5. (可选) 生成测试数据
python seed_test_data.py

# 6. 启动后端服务
python -m app.main
# 或
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
```

后端服务运行在 `http://localhost:3001`，API 文档访问 `http://localhost:3001/docs`。

### 前端服务

```bash
# 1. 进入前端目录
cd frontend

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，按需配置

# 3. 安装依赖
npm install

# 4. 启动开发服务器
npm run dev
```

访问 `http://localhost:5173`。

> **注意：** 前端开发服务器会自动将 `/api` 请求代理到后端 `http://localhost:3001`，请确保后端服务已启动。

默认账号：
| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin | 管理员 |
| user001 | 123456 | 普通用户 |

## Directory Structure

```
frontend/
├── .env.example             # 环境变量模板
├── index.html               # 入口 HTML
├── package.json             # 前端依赖 & 脚本
├── vite.config.js           # Vite 配置（含 /api 代理）
├── tailwind.config.js       # Tailwind CSS 配置
├── src/
│   ├── App.vue              # Root: auth guard + tab navigation
│   ├── main.js              # Entry: mount app, init Pinia
│   ├── style.css            # Tailwind directives + custom animations
│   ├── api/
│   │   ├── stock.js         # 后端 API 对接（交易、持仓、用户等）
│   │   └── stock-quote.js   # 股票行情 API（搜索、实时报价）
│   ├── stores/
│   │   ├── stock.js         # Pinia store (state, actions, modals)
│   │   ├── stocks.js        # Pinia store（股票搜索状态）
│   │   ├── watchlist.js     # Pinia store（自选股、定时刷新）
│   │   ├── contract.js      # Pinia store（合约管理）
│   │   ├── allocator.js     # Pinia store（持仓比例分析）
│   │   └── allocator2.js    # Pinia store（持仓比例分析 v2）
│   └── components/
│       ├── common/               # 全局公用组件
│       │   ├── ConfirmModal.vue  # 确认弹窗
│       │   └── Toast.vue        # Toast 通知
│       ├── layout/               # 布局组件
│       │   └── Sidebar.vue      # 侧边栏导航
│       ├── auth/                 # 认证相关
│       │   ├── LoginPage.vue    # 登录 / 注册
│       │   └── ChangePasswordForm.vue # 修改密码
│       ├── trade/                # 网格交易页
│       │   ├── TradeList.vue    # 交易记录列表
│       │   ├── TradeModal.vue   # 添加/编辑交易弹窗
│       │   ├── SellModal.vue    # 卖出弹窗
│       │   ├── PositionList.vue # 持仓概览
│       │   └── QuickTrade.vue   # 快捷交易标签
│       ├── stocks/               # 我的自选页
│       │   ├── StockSearch.vue  # 搜索主页面
│       │   ├── SearchBar.vue    # 搜索输入框（防抖）
│       │   ├── StockGrid.vue    # 搜索结果网格
│       │   ├── StockCard.vue    # 股票卡片
│       │   ├── StockDetailModal.vue # 股票详情弹窗
│       │   └── WatchlistPanel.vue   # 自选股面板
│       ├── portfolio/            # 持仓比例页
│       │   ├── PortfolioRatio.vue   # 持仓比例分析页
│       │   ├── PortfolioModal.vue   # 添加持仓比例项弹窗
│       │   ├── PortfolioAllocator.vue  # 持仓分配可视化
│       │   └── PortfolioAllocator2.vue # 持仓分配可视化 v2
│       ├── contract/             # 合约管理页
│       │   └── ContractManagement.vue
│       ├── admin/                # 用户管理页
│       │   └── UserManagement.vue
│       └── sponsor/              # 赞助页
│           └── SponsorView.vue
backend/
└── ...                      # 后端服务（见 backend/README.md）
```

## Database

MySQL 数据库，建表语句见 `backend/sql/schema.sql`。核心表设计：

- **`fnos_trades`** — 交易记录，通过 `buy_order_no` 关联买卖，`user_id` 隔离用户数据
- **`fnos_positions`** — 持仓表，按用户+合约唯一，后端服务自动重算
- **`fnos_trade_tags`** — 快捷交易标签，买入时自动创建，按用户隔离
- **`fnos_portfolio_items`** — 持仓比例数据源（名称、合约、标签、金额），按用户隔离
- **`fnos_stocks`** — 股票行情历史数据
- **`fnos_watchlist`** — 自选股列表

所有业务表通过 `user_id` 实现多租户数据隔离，每个用户只能访问自己的数据。

## Deployment

详细部署文档请参考 [DEPLOY.md](./DEPLOY.md)

### 快速部署

**前端打包：**

```bash
cd frontend
npm install
npm run build
```

**后端启动：**

```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

### GitHub Pages 自动部署

Push to GitHub. GitHub Actions builds and deploys to GitHub Pages automatically.

1. 在仓库 Settings → Actions secrets 添加前端所需的环境变量
2. 推送 main 分支即可
