-- TradeFlow Server - Supabase 建表语句
-- 在 Supabase Dashboard → SQL Editor 执行

-- 股票行情快照（每次查询自动更新）
CREATE TABLE IF NOT EXISTS stocks (
  code              TEXT PRIMARY KEY,
  name              TEXT,
  price             NUMERIC,
  changePercent     NUMERIC,
  open              NUMERIC,
  high              NUMERIC,
  low               NUMERIC,
  yesterday         NUMERIC,
  volume            NUMERIC,
  amount            NUMERIC,
  amplitude         NUMERIC,
  turnoverRate      NUMERIC,
  totalMarketCap    NUMERIC,
  source            TEXT,
  updated_at        TIMESTAMP DEFAULT NOW()
);

-- 自选股
CREATE TABLE IF NOT EXISTS watchlist (
  id        SERIAL PRIMARY KEY,
  code      TEXT NOT NULL UNIQUE,
  name      TEXT NOT NULL,
  added_at  TIMESTAMP DEFAULT NOW()
);
