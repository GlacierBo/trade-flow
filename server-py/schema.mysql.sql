-- TradeFlow Server - MySQL 建表语句

-- 股票历史行情（搜索/定时任务写入，每只股票多条记录）
CREATE TABLE IF NOT EXISTS fnos_stocks (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  code            TEXT NOT NULL,
  name            TEXT,
  price           DECIMAL,
  changePercent   DECIMAL,
  open            DECIMAL,
  high            DECIMAL,
  low             DECIMAL,
  yesterday       DECIMAL,
  volume          DECIMAL,
  amount          DECIMAL,
  amplitude       DECIMAL,
  turnoverRate    DECIMAL,
  totalMarketCap  DECIMAL,
  source          TEXT,
  created_at      TIMESTAMP DEFAULT NOW()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 注意：MySQL 不支持 IF NOT EXISTS 建索引，此处直接创建
CREATE INDEX idx_fnos_stocks_code ON fnos_stocks(code(255));
CREATE INDEX idx_fnos_stocks_code_time ON fnos_stocks(code(255), created_at DESC);

-- 自选股（一只股票一条记录）
CREATE TABLE IF NOT EXISTS fnos_watchlist (
  code      VARCHAR(255) PRIMARY KEY,
  name      TEXT NOT NULL,
  added_at  TIMESTAMP DEFAULT NOW()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
