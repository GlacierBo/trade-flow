-- ============================================
-- TradeFlow - 交易标签表 Schema
-- 用于快捷交易功能
-- ============================================

-- 4. 交易标签表 (stock_trade_tags)
CREATE TABLE IF NOT EXISTS stock_trade_tags (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    contract VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    latest_price DECIMAL(10, 4) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引优化
CREATE INDEX idx_stock_trade_tags_contract ON stock_trade_tags(contract);

-- 启用 RLS
ALTER TABLE stock_trade_tags ENABLE ROW LEVEL SECURITY;

-- 创建策略（允许所有操作）
CREATE POLICY "Allow all operations on stock_trade_tags" ON stock_trade_tags
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 触发器：自动更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_stock_trade_tags_updated_at
BEFORE UPDATE ON stock_trade_tags
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 5. 持仓比例计算表 (portfolio_items)
CREATE TABLE IF NOT EXISTS portfolio_items (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contract VARCHAR(20) NOT NULL,
    tag VARCHAR(50) DEFAULT '',
    price DECIMAL(12, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引优化
CREATE INDEX idx_portfolio_items_tag ON portfolio_items(tag);
CREATE INDEX idx_portfolio_items_contract ON portfolio_items(contract);

-- 启用 RLS
ALTER TABLE portfolio_items ENABLE ROW LEVEL SECURITY;

-- 创建策略（允许所有操作）
CREATE POLICY "Allow all operations on portfolio_items" ON portfolio_items
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 触发器：自动更新 updated_at
CREATE TRIGGER trg_portfolio_items_updated_at
BEFORE UPDATE ON portfolio_items
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 注释说明
COMMENT ON TABLE stock_trade_tags IS '交易标签表（快捷交易入口）';
COMMENT ON COLUMN stock_trade_tags.contract IS '合约代码（唯一）';
COMMENT ON COLUMN stock_trade_tags.name IS '合约名称';
COMMENT ON COLUMN stock_trade_tags.latest_price IS '最新价格（预留字段，后续由外部业务更新）';
COMMENT ON TABLE portfolio_items IS '持仓比例计算表';
COMMENT ON COLUMN portfolio_items.tag IS '分类标签（如白酒、科技等）';
