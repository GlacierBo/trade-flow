-- ============================================
-- TradeFlow - MySQL 建表语句
-- ============================================

-- ============================================
-- 已执行的建表语句
-- ============================================

-- 股票历史行情表（已执行）
CREATE TABLE IF NOT EXISTS fnos_stocks (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  code            VARCHAR(50) NOT NULL,
  name            VARCHAR(100),
  price           DECIMAL(18,2),
  changePercent   DECIMAL(18,2),
  open            DECIMAL(18,2),
  high            DECIMAL(18,2),
  low             DECIMAL(18,2),
  yesterday       DECIMAL(18,2),
  volume          DECIMAL,
  amount          DECIMAL,
  amplitude       DECIMAL(18,2),
  turnoverRate    DECIMAL(18,2),
  totalMarketCap  DECIMAL(18,2),
  source          VARCHAR(50),
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_code (code),
  INDEX idx_code_time (code, created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 自选股表（已执行）
CREATE TABLE IF NOT EXISTS fnos_watchlist (
  code      VARCHAR(50) PRIMARY KEY,
  name      VARCHAR(100) NOT NULL,
  added_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 未执行的建表语句
-- ============================================

-- 交易记录表（未执行）
CREATE TABLE IF NOT EXISTS fnos_trades (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  buy_order_no      VARCHAR(20),
  contract          VARCHAR(20) NOT NULL,
  name              VARCHAR(100) NOT NULL,
  price             DECIMAL(10,4) NOT NULL,
  shares            INT NOT NULL,
  remaining_shares  INT DEFAULT 0,
  amount            DECIMAL(12,2) NOT NULL,
  fee               DECIMAL(10,2) NOT NULL DEFAULT 0,
  net_amount        DECIMAL(12,2) NOT NULL,
  trade_type        VARCHAR(10) NOT NULL,
  trade_date        DATE NOT NULL DEFAULT (CURRENT_DATE),
  user_id           INT NOT NULL DEFAULT 1,
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  realized_profit   DECIMAL(12,2) DEFAULT 0,
  single_profit     DECIMAL(12,2) DEFAULT 0,
  INDEX idx_contract (contract),
  INDEX idx_buy_order_no (buy_order_no),
  INDEX idx_trade_type (trade_type),
  INDEX idx_created_at (created_at DESC),
  INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 持仓表（未执行）
CREATE TABLE IF NOT EXISTS fnos_positions (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  contract      VARCHAR(20) NOT NULL,
  name          VARCHAR(100) NOT NULL,
  user_id       INT NOT NULL DEFAULT 1,
  total_shares  INT NOT NULL DEFAULT 0,
  avg_cost      DECIMAL(10,4) DEFAULT 0,
  latest_price  DECIMAL(10,4) DEFAULT 0,
  market_value  DECIMAL(12,2) DEFAULT 0,
  profit        DECIMAL(12,2) DEFAULT 0,
  profit_rate   DECIMAL(8,2) DEFAULT 0,
  updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY idx_user_contract (user_id, contract),
  INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 流水号计数器表（未执行）
CREATE TABLE IF NOT EXISTS fnos_serial_counters (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  counter_date    VARCHAR(8) NOT NULL,
  current_serial  INT NOT NULL DEFAULT 0,
  UNIQUE KEY idx_counter_date (counter_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 持仓比例项目表（未执行）
CREATE TABLE IF NOT EXISTS fnos_portfolio_items (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(100) NOT NULL,
  contract    VARCHAR(50) NOT NULL,
  tag         VARCHAR(50) DEFAULT '',
  price       DECIMAL(18,2) NOT NULL DEFAULT 0,
  user_id     INT NOT NULL DEFAULT 1,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id),
  INDEX idx_contract (contract)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 交易标签表（未执行）
CREATE TABLE IF NOT EXISTS fnos_trade_tags (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  contract      VARCHAR(50) NOT NULL,
  name          VARCHAR(100) NOT NULL,
  latest_price  DECIMAL(18,2) DEFAULT 0,
  user_id       INT NOT NULL DEFAULT 1,
  updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY idx_user_contract (user_id, contract)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 用户表（未执行）
CREATE TABLE IF NOT EXISTS fnos_users (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  username    VARCHAR(50) NOT NULL,
  password    VARCHAR(255) NOT NULL,
  salt        VARCHAR(32) NOT NULL,
  role        VARCHAR(20) NOT NULL DEFAULT 'user',
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 默认用户种子数据（未执行）
-- admin 密码: admin, user001 密码: 123456
INSERT INTO fnos_users (username, password, salt, role) VALUES
  ('admin', MD5(CONCAT('admin', 'a1b2c3d4e5f6g7h8')), 'a1b2c3d4e5f6g7h8', 'admin'),
  ('user001', MD5(CONCAT('123456', 'u1u2u3u4u5u6u7u8')), 'u1u2u3u4u5u6u7u8', 'user')
ON DUPLICATE KEY UPDATE username=username;

-- 合约管理表（未执行）
CREATE TABLE IF NOT EXISTS fnos_contracts (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  code        VARCHAR(20) NOT NULL,
  name        VARCHAR(100) NOT NULL,
  user_id     INT NOT NULL DEFAULT 1,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY idx_user_code (user_id, code),
  INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
