-- ============================================
-- TradeFlow - MySQL 建表语句
-- ============================================

-- ============================================
-- 已执行的建表语句
-- ============================================

-- 股票历史行情表（已执行）
CREATE TABLE IF NOT EXISTS fnos_stocks (
  id              INT AUTO_INCREMENT PRIMARY KEY        COMMENT '主键',
  code            VARCHAR(50) NOT NULL                  COMMENT '股票代码，如 SH510500',
  name            VARCHAR(100)                          COMMENT '股票名称',
  price           DECIMAL(18,2)                         COMMENT '最新价',
  changePercent   DECIMAL(18,2)                         COMMENT '涨跌幅 (%)',
  open            DECIMAL(18,2)                         COMMENT '开盘价',
  high            DECIMAL(18,2)                         COMMENT '最高价',
  low             DECIMAL(18,2)                         COMMENT '最低价',
  yesterday       DECIMAL(18,2)                         COMMENT '昨收价',
  volume          DECIMAL                               COMMENT '成交量',
  amount          DECIMAL                               COMMENT '成交额',
  amplitude       DECIMAL(18,2)                         COMMENT '振幅 (%)',
  turnoverRate    DECIMAL(18,2)                         COMMENT '换手率 (%)',
  totalMarketCap  DECIMAL(18,2)                         COMMENT '总市值',
  source          VARCHAR(50)                           COMMENT '数据来源 (eastmoney/sina)',
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP   COMMENT '创建时间',
  INDEX idx_code (code),
  INDEX idx_code_time (code, created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票历史行情表';

-- 自选股表（已执行）
CREATE TABLE IF NOT EXISTS fnos_watchlist (
  code      VARCHAR(50) PRIMARY KEY                     COMMENT '股票代码',
  name      VARCHAR(100) NOT NULL                       COMMENT '股票名称',
  added_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP         COMMENT '添加时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自选股表';

-- ============================================
-- 未执行的建表语句
-- ============================================

-- 交易记录表（未执行）
CREATE TABLE IF NOT EXISTS fnos_trades (
  id                INT AUTO_INCREMENT PRIMARY KEY        COMMENT '主键',
  buy_order_no      VARCHAR(20)                          COMMENT '买入单号 (NOYYYYMMDDNNNN)',
  contract          VARCHAR(20) NOT NULL                  COMMENT '合约代码',
  name              VARCHAR(100) NOT NULL                 COMMENT '合约名称',
  price             DECIMAL(10,4) NOT NULL                COMMENT '交易价格',
  shares            INT NOT NULL                          COMMENT '份额 (正=买入, 负=卖出)',
  remaining_shares  INT DEFAULT 0                         COMMENT '剩余可卖份额',
  amount            DECIMAL(12,2) NOT NULL                COMMENT '成交金额',
  fee               DECIMAL(10,2) NOT NULL DEFAULT 0      COMMENT '佣金',
  net_amount        DECIMAL(12,2) NOT NULL                COMMENT '净额 (含佣金)',
  trade_type        VARCHAR(10) NOT NULL                  COMMENT '交易类型 (buy/sell)',
  trade_date        DATE NOT NULL DEFAULT (CURRENT_DATE)  COMMENT '交易日期',
  user_id           INT NOT NULL DEFAULT 1                COMMENT '用户ID',
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP   COMMENT '创建时间',
  realized_profit   DECIMAL(12,2) DEFAULT 0               COMMENT '已实现收益 (买入记录累计)',
  single_profit     DECIMAL(12,2) DEFAULT 0               COMMENT '单笔收益 (卖出记录)',
  INDEX idx_contract (contract),
  INDEX idx_buy_order_no (buy_order_no),
  INDEX idx_trade_type (trade_type),
  INDEX idx_created_at (created_at DESC),
  INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易记录表';

-- 持仓表（未执行）
CREATE TABLE IF NOT EXISTS fnos_positions (
  id            INT AUTO_INCREMENT PRIMARY KEY                       COMMENT '主键',
  contract      VARCHAR(20) NOT NULL                                 COMMENT '合约代码',
  name          VARCHAR(100) NOT NULL                                COMMENT '合约名称',
  user_id       INT NOT NULL DEFAULT 1                               COMMENT '用户ID',
  total_shares  INT NOT NULL DEFAULT 0                               COMMENT '持仓份额',
  avg_cost      DECIMAL(10,4) DEFAULT 0                              COMMENT '平均成本',
  latest_price  DECIMAL(10,4) DEFAULT 0                              COMMENT '最新价格',
  market_value  DECIMAL(12,2) DEFAULT 0                              COMMENT '市值',
  profit        DECIMAL(12,2) DEFAULT 0                              COMMENT '已实现收益',
  profit_rate   DECIMAL(8,2) DEFAULT 0                               COMMENT '收益率 (%)',
  updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE KEY idx_user_contract (user_id, contract),
  INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='持仓表';

-- 流水号计数器表（未执行）
CREATE TABLE IF NOT EXISTS fnos_serial_counters (
  id              INT AUTO_INCREMENT PRIMARY KEY        COMMENT '主键',
  counter_date    VARCHAR(8) NOT NULL                   COMMENT '日期 (YYYYMMDD)',
  current_serial  INT NOT NULL DEFAULT 0                COMMENT '当前流水号',
  UNIQUE KEY idx_counter_date (counter_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='流水号计数器表';

-- 持仓比例项目表（未执行）
CREATE TABLE IF NOT EXISTS fnos_portfolio_items (
  id          INT AUTO_INCREMENT PRIMARY KEY        COMMENT '主键',
  name        VARCHAR(100) NOT NULL                  COMMENT '名称',
  contract    VARCHAR(50) NOT NULL                   COMMENT '合约代码',
  tag         VARCHAR(50) DEFAULT ''                 COMMENT '分类标签 (如白酒、科技)',
  price       DECIMAL(18,2) NOT NULL DEFAULT 0       COMMENT '金额',
  user_id     INT NOT NULL DEFAULT 1                 COMMENT '用户ID',
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP    COMMENT '创建时间',
  INDEX idx_user_id (user_id),
  INDEX idx_contract (contract)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='持仓比例项目表';

-- 交易标签表（未执行）
CREATE TABLE IF NOT EXISTS fnos_trade_tags (
  id            INT AUTO_INCREMENT PRIMARY KEY                               COMMENT '主键',
  contract      VARCHAR(50) NOT NULL                                          COMMENT '合约代码',
  name          VARCHAR(100) NOT NULL                                         COMMENT '合约名称',
  latest_price  DECIMAL(18,2) DEFAULT 0                                      COMMENT '最新价格',
  user_id       INT NOT NULL DEFAULT 1                                       COMMENT '用户ID',
  updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE KEY idx_user_contract (user_id, contract)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易标签表（快捷交易入口）';

-- 用户表（未执行）
CREATE TABLE IF NOT EXISTS fnos_users (
  id          INT AUTO_INCREMENT PRIMARY KEY                               COMMENT '主键',
  username    VARCHAR(50) NOT NULL                                          COMMENT '用户名',
  password    VARCHAR(255) NOT NULL                                         COMMENT '密码 (MD5+盐值加密)',
  salt        VARCHAR(32) NOT NULL                                          COMMENT '盐值',
  role        VARCHAR(20) NOT NULL DEFAULT 'user'                           COMMENT '角色 (admin/user)',
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP                           COMMENT '注册时间',
  updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE KEY idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 默认用户种子数据（未执行）
-- admin 密码: admin, user001 密码: 123456
INSERT INTO fnos_users (username, password, salt, role) VALUES
  ('admin', MD5(CONCAT('admin', 'a1b2c3d4e5f6g7h8')), 'a1b2c3d4e5f6g7h8', 'admin'),
  ('user001', MD5(CONCAT('123456', 'u1u2u3u4u5u6u7u8')), 'u1u2u3u4u5u6u7u8', 'user')
ON DUPLICATE KEY UPDATE username=username;

-- 合约管理表（未执行）
CREATE TABLE IF NOT EXISTS fnos_contracts (
  id          INT AUTO_INCREMENT PRIMARY KEY        COMMENT '主键',
  code        VARCHAR(20) NOT NULL                  COMMENT '合约代码',
  name        VARCHAR(100) NOT NULL                 COMMENT '合约名称',
  user_id     INT NOT NULL DEFAULT 1                COMMENT '用户ID',
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP   COMMENT '创建时间',
  UNIQUE KEY idx_user_code (user_id, code),
  INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='合约管理表';
