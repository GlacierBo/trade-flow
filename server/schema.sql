-- TradeFlow Server - Supabase 建表语句
-- 在 Supabase Dashboard → SQL Editor 执行

-- 股票历史行情（搜索/定时任务写入，每只股票多条记录）
CREATE TABLE IF NOT EXISTS fnos_stocks (
  id              SERIAL PRIMARY KEY,
  code            TEXT NOT NULL,
  name            TEXT,
  price           NUMERIC,
  changePercent   NUMERIC,
  open            NUMERIC,
  high            NUMERIC,
  low             NUMERIC,
  yesterday       NUMERIC,
  volume          NUMERIC,
  amount          NUMERIC,
  amplitude       NUMERIC,
  turnoverRate    NUMERIC,
  totalMarketCap  NUMERIC,
  source          TEXT,
  created_at      TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_fnos_stocks_code ON fnos_stocks(code);
CREATE INDEX IF NOT EXISTS idx_fnos_stocks_code_time ON fnos_stocks(code, created_at DESC);

-- 自选股（一只股票一条记录）
CREATE TABLE IF NOT EXISTS fnos_watchlist (
  code      TEXT PRIMARY KEY,
  name      TEXT NOT NULL,
  added_at  TIMESTAMP DEFAULT NOW()
);
