# TradeFlow — 股票交易管理系统

## 项目简介

TradeFlow 是一个个人股票交易管理系统，支持买入/卖出记录管理、持仓盈亏计算、数据持久化存储。

**技术特点**：
- ✅ **无后端服务**：直接使用 Supabase（PostgreSQL + Auto API）
- ✅ **自动部署**：GitHub Actions 自动构建并部署到 GitHub Pages
- ✅ **网格交易**：支持基于特定买入记录的卖出操作，实现成本摊薄
- ✅ **全量重算**：持仓数据基于所有交易记录实时计算，确保准确性
- ✅ **登录认证**：简单的用户名密码登录保护
- ✅ **快捷交易**：标签化常用合约，一键快速发起交易

---

## 🚀 快速开始

### 前置条件

1. **创建 Supabase 项目**
   - 访问 [https://app.supabase.com](https://app.supabase.com)
   - 创建新项目，获取 Project URL 和 Anon Key

2. **执行数据库 Schema**
   - 在 Supabase Dashboard → SQL Editor
   - 复制 `supabase-schema.sql` 全部内容并执行

### 本地开发

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 Supabase 配置

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

访问 http://localhost:5173，使用默认账号登录：
- **用户名**: `admin`
- **密码**: `admin`

### 生产部署

推送代码到 GitHub 后，GitHub Actions 会自动构建并部署到 GitHub Pages。

**配置步骤**：
1. 在仓库 Settings → Secrets and variables → Actions 中添加：
   - `VITE_SUPABASE_URL` = 你的 Supabase URL
   - `VITE_SUPABASE_ANON_KEY` = 你的 Supabase Anon Key
2. 在 Settings → Pages 中启用 GitHub Actions
3. 推送代码到 main 分支

部署完成后访问：`https://username.github.io/repository-name`

---

## 技术架构

| 层级 | 技术 | 说明 |
|------|------|------|
| 数据库 | PostgreSQL (Supabase) | 云端数据库 + 自动 API |
| 前端框架 | Vue 3 + Vite + Pinia | 现代化 SPA 应用 |
| CSS | Tailwind CSS | 原子化样式 |
| 状态管理 | Pinia | 轻量级状态管理 |
| 部署 | GitHub Actions → GitHub Pages | 自动化 CI/CD |

---

## 目录结构

```
PythonProject/
├── src/                        # Vue 3 前端源码
│   ├── App.vue                 # 根组件（含登录逻辑）
│   ├── api/stock.js            # Supabase Client 封装
│   ├── stores/stock.js         # Pinia store（含认证状态）
│   └── components/             # Vue 组件
│       ├── LoginPage.vue       # 登录页面
│       ├── TradeList.vue       # 交易明细列表
│       ├── PositionList.vue    # 持仓概览
│       ├── TradeModal.vue      # 新增交易弹窗
│       ├── SellModal.vue       # 卖出操作弹窗
│       ├── ConfirmModal.vue    # 确认对话框
│       └── Toast.vue           # 消息提示
├── public/
│   └── favicon.svg             # 网站图标
├── .env.example                # 环境变量模板
├── package.json                # 项目依赖
├── supabase-schema.sql         # PostgreSQL 数据库 schema
└── .github/workflows/deploy.yml # GitHub Actions 配置
```

---

## 核心功能

### 交易管理

#### 买入操作
- 自动生成买入单号（格式：`NO + YYYYMMDD + 4位流水号`）
- 记录合约代码、名称、价格、份额、手续费
- 触发器自动更新持仓（全量重算）

#### 卖出操作
- 必须关联买入单号，支持分批卖出
- 验证卖出数量不超过剩余可卖份额
- 计算单笔收益：`(卖出价 - 买入价) × 份额 - 手续费`
- 自动更新买入记录的剩余份额和累计收益

#### 删除操作
- 买入记录有卖出关联时禁止删除（需先删除所有卖出记录）
- 删除卖出记录自动恢复买入记录的可卖份额和收益
- 触发器自动重新计算持仓

### 持仓计算（全量重算机制）

- 基于所有交易记录实时统计，不依赖增量更新
- **成本计算公式**：`(买入总金额 - 卖出总金额) / 持仓份额`
- **已实现收益**：所有卖出记录的 single_profit 汇总
- **未实现收益率**：`(现价 - 成本) / 净成本 × 100%`
- 每次交易变动自动触发重算，确保数据准确性

### 快捷交易

- 标签化常用合约，快速发起交易
- 自动记录买入过的合约，生成快捷入口
- 点击标签自动填充合约信息（代码、名称）
- 支持删除不需要的标签
- 预留实时价格字段，后续可扩展行情功能

### 登录认证

- 简单的用户名密码登录（默认：admin/admin）
- 登录状态保存到 localStorage
- 刷新页面保持登录状态
- 右上角显示用户名和退出按钮

---

## 数据库设计

### stock_trades（交易记录表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| buy_order_no | VARCHAR(20) | 买入单号，买入和关联卖出共用 |
| contract | VARCHAR(20) | 合约代码 |
| name | VARCHAR(100) | 合约名称 |
| price | DECIMAL(10, 4) | 交易价格 |
| shares | INTEGER | 买入正数，卖出负数 |
| remaining_shares | INTEGER | 剩余可卖份额（仅买入记录） |
| amount | DECIMAL(12, 2) | 成交金额 |
| fee | DECIMAL(10, 2) | 手续费 |
| trade_type | VARCHAR(10) | "buy" 或 "sell" |
| realized_profit | DECIMAL(12, 2) | 累计已实现收益（仅买入记录） |
| single_profit | DECIMAL(12, 2) | 单笔收益（仅卖出记录） |

### stock_positions（持仓表）
通过 PostgreSQL 函数 `recalculate_position()` 自动计算，无需手动维护。

### daily_serial_counters（流水号计数器）
确保买入单号的全局唯一性，每天从 0001 开始递增。

### stock_trade_tags（交易标签表）
存储用户买入过的合约，提供快捷交易入口。包含合约代码、名称、最新价格等字段。
每次买入交易后自动创建/更新标签，按更新时间倒序排列。

---

**祝你使用愉快！** 🎉
