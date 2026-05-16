-- ============================================
-- TradeFlow - Supabase Database Schema
-- ============================================

-- 1. 交易记录表 (stock_trades)
CREATE TABLE IF NOT EXISTS stock_trades (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    buy_order_no VARCHAR(20),
    contract VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 4) NOT NULL,
    shares INTEGER NOT NULL,
    remaining_shares INTEGER DEFAULT 0,
    amount DECIMAL(12, 2) NOT NULL,
    fee DECIMAL(10, 2) NOT NULL DEFAULT 0,
    net_amount DECIMAL(12, 2) NOT NULL,
    trade_type VARCHAR(10) NOT NULL CHECK (trade_type IN ('buy', 'sell')),
    trade_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    realized_profit DECIMAL(12, 2) DEFAULT 0,
    single_profit DECIMAL(12, 2) DEFAULT 0
);

-- 索引优化
CREATE INDEX idx_stock_trades_contract ON stock_trades(contract);
CREATE INDEX idx_stock_trades_buy_order_no ON stock_trades(buy_order_no);
CREATE INDEX idx_stock_trades_trade_type ON stock_trades(trade_type);
CREATE INDEX idx_stock_trades_created_at ON stock_trades(created_at DESC);

-- 2. 持仓表 (stock_positions)
CREATE TABLE IF NOT EXISTS stock_positions (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    contract VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    total_shares INTEGER NOT NULL DEFAULT 0,
    avg_cost DECIMAL(10, 4) DEFAULT 0,
    latest_price DECIMAL(10, 4) DEFAULT 0,
    market_value DECIMAL(12, 2) DEFAULT 0,
    profit DECIMAL(12, 2) DEFAULT 0,
    profit_rate DECIMAL(8, 2) DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引优化
CREATE INDEX idx_stock_positions_contract ON stock_positions(contract);

-- 3. 流水号计数器表 (daily_serial_counters)
CREATE TABLE IF NOT EXISTS daily_serial_counters (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    counter_date VARCHAR(8) UNIQUE NOT NULL, -- YYYYMMDD格式
    current_serial INTEGER NOT NULL DEFAULT 0
);

-- 索引优化
CREATE INDEX idx_daily_serial_counters_date ON daily_serial_counters(counter_date);

-- ============================================
-- 行级安全策略 (RLS)
-- ============================================

-- 启用 RLS
ALTER TABLE stock_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_serial_counters ENABLE ROW LEVEL SECURITY;

-- 创建策略（允许所有操作，因为是个人应用）
-- 如果需要用户认证，可以改为: USING (auth.uid() = user_id)
CREATE POLICY "Allow all operations on stock_trades" ON stock_trades
    FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow all operations on stock_positions" ON stock_positions
    FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow all operations on daily_serial_counters" ON daily_serial_counters
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- PostgreSQL 函数
-- ============================================

-- 函数1: 生成买入单号
CREATE OR REPLACE FUNCTION generate_buy_order_no(p_trade_date DATE)
RETURNS VARCHAR(20) AS $$
DECLARE
    v_date_str VARCHAR(8);
    v_counter RECORD;
    v_serial INTEGER;
    v_order_no VARCHAR(20);
BEGIN
    -- 转换日期为 YYYYMMDD 格式
    v_date_str := TO_CHAR(p_trade_date, 'YYYYMMDD');
    
    -- 查询或创建计数器
    SELECT * INTO v_counter
    FROM daily_serial_counters
    WHERE counter_date = v_date_str
    FOR UPDATE; -- 锁定行以防止并发问题
    
    IF FOUND THEN
        -- 已有记录，递增流水号
        UPDATE daily_serial_counters
        SET current_serial = current_serial + 1
        WHERE counter_date = v_date_str
        RETURNING current_serial INTO v_serial;
    ELSE
        -- 新的一天，创建新记录
        INSERT INTO daily_serial_counters (counter_date, current_serial)
        VALUES (v_date_str, 1)
        RETURNING current_serial INTO v_serial;
    END IF;
    
    -- 生成买入单号：NO + YYYYMMDD + 4位流水号
    v_order_no := 'NO' || v_date_str || LPAD(v_serial::TEXT, 4, '0');
    
    RETURN v_order_no;
END;
$$ LANGUAGE plpgsql;

-- 函数2: 重新计算持仓（全量重算）
CREATE OR REPLACE FUNCTION recalculate_position(p_contract VARCHAR)
RETURNS VOID AS $$
DECLARE
    v_total_buy_shares INTEGER := 0;
    v_total_buy_amount DECIMAL(12, 2) := 0;
    v_total_sell_shares INTEGER := 0;
    v_total_sell_amount DECIMAL(12, 2) := 0;
    v_position_shares INTEGER;
    v_net_cost DECIMAL(12, 2);
    v_avg_cost DECIMAL(10, 4);
    v_latest_price DECIMAL(10, 4);
    v_market_value DECIMAL(12, 2);
    v_total_profit DECIMAL(12, 2) := 0;
    v_unrealized_profit DECIMAL(12, 2);
    v_profit_rate DECIMAL(8, 2);
    v_name VARCHAR(100);
BEGIN
    -- 获取合约名称（从第一条交易记录）
    SELECT name INTO v_name
    FROM stock_trades
    WHERE contract = p_contract
    LIMIT 1;
    
    -- 计算总买入
    SELECT COALESCE(SUM(shares), 0), COALESCE(SUM(amount), 0)
    INTO v_total_buy_shares, v_total_buy_amount
    FROM stock_trades
    WHERE contract = p_contract AND trade_type = 'buy';
    
    -- 计算总卖出（取绝对值）
    SELECT COALESCE(SUM(ABS(shares)), 0), COALESCE(SUM(ABS(amount)), 0)
    INTO v_total_sell_shares, v_total_sell_amount
    FROM stock_trades
    WHERE contract = p_contract AND trade_type = 'sell';
    
    -- 计算持仓数量
    v_position_shares := v_total_buy_shares - v_total_sell_shares;

    -- 计算已实现收益（所有卖出的 single_profit 汇总）
    SELECT COALESCE(SUM(single_profit), 0)
    INTO v_total_profit
    FROM stock_trades
    WHERE contract = p_contract AND trade_type = 'sell';

    -- 如果持仓为零或负数，保留记录用于查看收益，标记为已平仓
    IF v_position_shares <= 0 THEN
        INSERT INTO stock_positions (contract, name, total_shares, avg_cost, latest_price, market_value, profit, profit_rate, updated_at)
        VALUES (p_contract, v_name, 0, 0, 0, 0, v_total_profit, 0, NOW())
        ON CONFLICT (contract) DO UPDATE SET
            name = EXCLUDED.name,
            total_shares = 0,
            avg_cost = 0,
            latest_price = 0,
            market_value = 0,
            profit = EXCLUDED.profit,
            profit_rate = 0,
            updated_at = NOW();
        RETURN;
    END IF;
    
    -- 计算净成本和平均成本
    v_net_cost := v_total_buy_amount - v_total_sell_amount;
    v_avg_cost := v_net_cost / v_position_shares;
    
    -- 获取最新价格（最后一笔交易的价格）
    SELECT price INTO v_latest_price
    FROM stock_trades
    WHERE contract = p_contract
    ORDER BY created_at DESC
    LIMIT 1;
    
    -- 计算市值
    v_market_value := v_position_shares * v_latest_price;
    
    -- 计算未实现盈亏和收益率
    v_unrealized_profit := (v_latest_price - v_avg_cost) * v_position_shares;
    v_profit_rate := CASE 
        WHEN v_net_cost > 0 THEN (v_unrealized_profit / v_net_cost * 100)
        ELSE 0
    END;
    
    -- 更新或创建持仓记录
    INSERT INTO stock_positions (
        contract, name, total_shares, avg_cost, latest_price,
        market_value, profit, profit_rate, updated_at
    )
    VALUES (
        p_contract, v_name, v_position_shares, v_avg_cost, v_latest_price,
        v_market_value, v_total_profit, v_profit_rate, NOW()
    )
    ON CONFLICT (contract) DO UPDATE SET
        name = EXCLUDED.name,
        total_shares = EXCLUDED.total_shares,
        avg_cost = EXCLUDED.avg_cost,
        latest_price = EXCLUDED.latest_price,
        market_value = EXCLUDED.market_value,
        profit = EXCLUDED.profit,
        profit_rate = EXCLUDED.profit_rate,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 触发器：自动重新计算持仓
-- ============================================

-- 创建触发器函数
CREATE OR REPLACE FUNCTION trigger_recalculate_position()
RETURNS TRIGGER AS $$
DECLARE
    v_contract VARCHAR;
BEGIN
    -- 确定需要重新计算的合约
    IF TG_OP = 'DELETE' THEN
        v_contract := OLD.contract;
    ELSE
        v_contract := NEW.contract;
    END IF;
    
    -- 调用重算函数
    PERFORM recalculate_position(v_contract);
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 在交易表上创建触发器
CREATE TRIGGER trg_stock_trades_recalc
AFTER INSERT OR UPDATE OR DELETE ON stock_trades
FOR EACH ROW
EXECUTE FUNCTION trigger_recalculate_position();

-- ============================================
-- 注释说明
-- ============================================

COMMENT ON TABLE stock_trades IS '股票交易记录表';
COMMENT ON TABLE stock_positions IS '股票持仓表（自动计算）';
COMMENT ON TABLE daily_serial_counters IS '每日流水号计数器';
COMMENT ON FUNCTION generate_buy_order_no(DATE) IS '生成买入单号：NO+YYYYMMDD+4位流水号';
COMMENT ON FUNCTION recalculate_position(VARCHAR) IS '全量重算持仓数据';
