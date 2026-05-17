# 需求文档

## 项目概述

TradeFlow 是一个网格交易记录 + 持仓比例分析工具，帮助用户追踪每笔网格交易的盈利情况并管理资产配置。

## 功能需求

### 1. Tab 导航

页面顶部蓝色按钮组 Tab，切换"网格交易"和"持仓比例"两个页面。

- 当前 Tab 高亮蓝色，非活跃 Tab 灰色
- 切换时仅切换显示内容，不重新加载全局数据

### 2. 网格交易页

#### 2.1 布局

左右结构 2:6:4（左侧快捷交易 / 中间交易明细 / 右侧持仓概览）。

#### 2.2 买入操作

- 自动生成买入单号（格式：`NO + YYYYMMDD + 4位流水号`）
- 记录字段：合约代码、合约名称、交易价格、交易份额、手续费率
- 买入时自动创建/更新快捷交易标签（`stock_trade_tags`）

#### 2.3 卖出操作（网格核心）

- 必须关联买入单号，明确卖出对应哪次买入
- 支持分批卖出（一笔买入可对应多笔卖出）
- 自动计算单笔收益：`(卖出价 - 买入价) × 份额 - 手续费`

#### 2.4 删除操作

- 买入记录有卖出关联时禁止删除（需先删除所有卖出记录）
- 删除卖出记录自动恢复买入记录的可卖份额和收益

#### 2.5 持仓概览

- 展示所有当前持有仓位（持仓数量、成本、现价、收益）
- **已平仓记录保留**：完全卖出后不会删除，显示为"已平仓"状态，展示累计收益
- 支持修改现价实时计算浮动盈亏
- 一键清仓操作（删除所有关联交易记录）

#### 2.6 快捷交易

- 左侧快捷列表展示所有已存合约标签（名称+代码）
- 点击标签自动填充新增交易弹窗的合约代码和名称（价格留空）
- 支持删除标签
- 标签在买入时自动创建

#### 2.7 交易明细

- 展示所有买入记录及其关联的卖出记录
- 支持按合约代码、名称、单号搜索

### 3. 持仓比例页

#### 3.1 布局

左右结构 2:8（左侧"合约"快捷列表 / 右侧比例计算）。

#### 3.2 新增弹窗（PortfolioModal）

- 字段：名称、代码、Tag（自由输入，支持 `<datalist>` 自动补全已有 Tag）、价格
- 点击左侧已存合约可预填充名称、代码、Tag，价格留空
- 保存后在左侧创建快捷入口

#### 3.3 右侧计算展示

- **总计置顶**：页面顶部显示总金额 + 100%
- **按 Tag 分组**：同一标签下的合约汇总，显示小计金额和占比
- **每个子项**：名称 + 代码 + 金额 + 占总计百分比
- **进度条底色**：每个子项根据占总计百分比从左侧画出彩色条
  - ≥ 80%：红色底色 (`bg-red-500/15`)
  - < 30%：蓝色底色 (`bg-blue-500/15`)
  - 30%~80%：灰色底色 (`bg-gray-500/10`)
- **金额显隐**：SVG 眼睛图标切换显示/隐藏金额（隐藏时替换为 `****`）
- 数量/价格列宽固定对齐

#### 3.4 数据持久化

持仓比例数据保存到 Supabase 独立表 `portfolio_items`，刷新不丢失。
左侧合约列表通过 `portfolio_items` 去重派生。

#### 3.5 累加逻辑

新增持仓项目时，如果合约代码已存在，自动将价格累加到现有记录中，而非创建重复记录。
更新时同步刷新名称和 Tag。

### 4. 认证

#### 4.1 注册

- 仅需用户名注册，验证用户名格式（正则：`/^[a-zA-Z0-9]+$/`，仅支持字母和数字）
- 密码由服务端自动生成（12位随机十六进制字符串）
- 使用 MD5 + 盐值加密存储
- 注册成功后一次性展示生成的密码，提示用户登录后修改密码
- 禁止重复用户名注册

#### 4.2 登录

- 使用用户名 + 密码登录
- 验证通过服务端 RPC 函数完成（MD5(salt || password) 比对）
- 登录状态保存到 localStorage（username、role、userId）
- 刷新页面保持登录状态

#### 4.3 修改密码

- 登录后右上角"修改密码"按钮
- 需验证原密码
- 新密码至少 6 位
- 新密码同样 MD5 + 盐值加密存储

#### 4.4 用户管理（管理员）

- Tab 导航增加"用户管理"入口，仅 `role=admin` 可见
- 展示所有注册用户列表（ID、用户名、角色、注册时间）
- 支持分页（每页 20 条）
- 管理员可重置任意用户密码为 `123456`
- 重置后页面展示新密码一次

#### 4.5 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin | admin |
| user001 | 123456 | user |

#### 4.6 权限

- `user` 角色：使用网格交易、持仓比例功能
- `admin` 角色：在 user 基础上增加用户管理权限

### 5. 数据库表结构

#### stock_trades — 交易记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER GENERATED ALWAYS AS IDENTITY | 主键 |
| buy_order_no | VARCHAR(20) | 买入单号（买入生成，卖出关联） |
| contract | VARCHAR(20) | 合约代码 |
| name | VARCHAR(100) | 合约名称 |
| price | DECIMAL(10, 4) | 交易价格 |
| shares | INTEGER | 份额（买入正数，卖出负数） |
| remaining_shares | INTEGER | 剩余可卖份额 |
| amount | DECIMAL(12, 2) | 成交金额 |
| fee | DECIMAL(10, 2) | 手续费 |
| net_amount | DECIMAL(12, 2) | 净额 |
| trade_type | VARCHAR(10) | 'buy' 或 'sell' |
| realized_profit | DECIMAL(12, 2) | 累计已实现收益 |
| single_profit | DECIMAL(12, 2) | 单笔收益（仅卖出） |
| user_id | INTEGER | 所属用户 ID，关联 app_users(id) |

#### stock_positions — 持仓表

触发器自动维护，每次交易变动全量重算。每个用户每合约一条记录。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER GENERATED ALWAYS AS IDENTITY | 主键 |
| contract | VARCHAR(20) | 合约代码 |
| name | VARCHAR(100) | 合约名称 |
| user_id | INTEGER | 所属用户 ID |
| total_shares | INTEGER | 总持仓（=0 表示已平仓） |
| avg_cost | DECIMAL(10, 4) | 平均成本 |
| latest_price | DECIMAL(10, 4) | 最新价格 |
| market_value | DECIMAL(12, 2) | 市值 |
| profit | DECIMAL(12, 2) | 累计收益 |
| profit_rate | DECIMAL(8, 2) | 收益率 |

唯一约束：`(user_id, contract)`

#### stock_trade_tags — 交易标签表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER GENERATED ALWAYS AS IDENTITY | 主键 |
| contract | VARCHAR(20) | 合约代码 |
| name | VARCHAR(100) | 合约名称 |
| latest_price | DECIMAL(10, 4) | 最新价格（预留） |
| user_id | INTEGER | 所属用户 ID |

唯一约束：`(user_id, contract)`

#### portfolio_items — 持仓比例表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER GENERATED ALWAYS AS IDENTITY | 主键 |
| name | VARCHAR(100) | 合约名称 |
| contract | VARCHAR(20) | 合约代码 |
| tag | VARCHAR(50) | 分类标签（如白酒、科技） |
| price | DECIMAL(12, 2) | 价格/金额 |
| user_id | INTEGER | 所属用户 ID |

#### app_users — 用户表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER GENERATED ALWAYS AS IDENTITY | 主键 |
| username | VARCHAR(50) UNIQUE | 用户名（登录账号） |
| password | VARCHAR(255) | MD5(salt + password) |
| salt | VARCHAR(32) | 盐值 |
| role | VARCHAR(20) | 角色：user / admin |
| created_at | TIMESTAMP WITH TIME ZONE | 注册时间 |

### 6. 数据库 RPC 函数

| 函数 | 参数 | 说明 |
|------|------|------|
| verify_user | p_username, p_password | 验证登录，返回用户信息或 NULL |
| register_user | p_username | 注册用户，自动生成密码，返回密码 |
| change_password | p_user_id, p_old_password, p_new_password | 修改密码 |
| reset_user_password | p_user_id | 管理员重置密码为 123456 |
| get_users | p_page, p_page_size | 分页获取用户列表 |
| recalculate_position | p_contract, p_user_id | 按用户重算指定合约的持仓 |

### 7. 数据库触发器

- 交易表 `AFTER INSERT OR UPDATE OR DELETE` → `recalculate_position(contract, user_id)` 按用户全量重算持仓
- 持仓比例表 `BEFORE UPDATE` → 自动更新 `updated_at`
- 用户表 `BEFORE UPDATE` → 自动更新 `updated_at`

### 9. 数据隔离

所有业务表（`stock_trades`、`stock_positions`、`stock_trade_tags`、`portfolio_items`）通过 `user_id` 列实现多用户数据隔离：

- 创建/写入时自动记录当前用户的 ID
- 查询时只返回当前用户的数据
- 更新/删除时校验所有权
- RLS 策略使用 `current_setting('app.current_user_id')` 确保数据库层隔离
- 前端在每次 API 调用中显式传入 `userId`（从登录态中获取）

该方案支持多用户独立使用，用户 A 看不到用户 B 的任何数据。
