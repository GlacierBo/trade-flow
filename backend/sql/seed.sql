-- ============================================
-- TradeFlow - 测试数据
-- ============================================

-- 清空旧数据
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE fnos_contracts;
TRUNCATE TABLE fnos_trades;
TRUNCATE TABLE fnos_positions;
TRUNCATE TABLE fnos_serial_counters;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 合约管理 (user_id=1)
-- ============================================
INSERT INTO fnos_contracts (code, name, user_id) VALUES
('601318', '中国平安', 1),
('600519', '贵州茅台', 1),
('600036', '招商银行', 1),
('002594', '比亚迪', 1),
('300750', '宁德时代', 1);

-- ============================================
-- 合约管理 (user_id=5)
-- ============================================
INSERT INTO fnos_contracts (code, name, user_id) VALUES
('510300', '沪深300ETF', 5),
('510500', '中证500ETF', 5),
('510050', '上证50ETF', 5),
('512100', '中证1000ETF', 5),
('159915', '创业板ETF', 5),
('588000', '科创50ETF', 5),
('512880', '证券ETF', 5),
('512010', '医药ETF', 5),
('515030', '新能源ETF', 5),
('512690', '酒ETF', 5),
('515790', '光伏ETF', 5),
('512660', '军工ETF', 5),
('600519', '贵州茅台', 5),
('601318', '中国平安', 5),
('000858', '五粮液', 5),
('600036', '招商银行', 5),
('002594', '比亚迪', 5),
('300750', '宁德时代', 5),
('601899', '紫金矿业', 5),
('000333', '美的集团', 5);

-- ============================================
-- 流水号计数器
-- ============================================
INSERT INTO fnos_serial_counters (counter_date, current_serial) VALUES
('20260602', 3),
('20260601', 3),
('20260531', 3),
('20260530', 3),
('20260529', 3);

-- ============================================
-- 交易记录 (user_id=1)
-- ============================================

-- 中国平安：2笔买入，1笔部分卖出
INSERT INTO fnos_trades (buy_order_no, contract, name, price, shares, remaining_shares, amount, fee, net_amount, trade_type, trade_date, user_id, realized_profit, single_profit) VALUES
('T20260528001', '601318', '中国平安', 52.30, 500, 200, 26150.00, 7.85, 26157.85, 'buy', '2026-05-28', 1, 0, 0),
('T20260528001', '601318', '中国平安', 54.80, 300, 0, 16440.00, 4.93, 16435.07, 'sell', '2026-05-30', 1, 737.22, 737.22),
('T20260529001', '601318', '中国平安', 51.50, 400, 400, 20600.00, 6.18, 20606.18, 'buy', '2026-05-29', 1, 0, 0);

-- 贵州茅台：1笔买入
INSERT INTO fnos_trades (buy_order_no, contract, name, price, shares, remaining_shares, amount, fee, net_amount, trade_type, trade_date, user_id, realized_profit, single_profit) VALUES
('T20260527001', '600519', '贵州茅台', 1680.00, 100, 100, 168000.00, 50.40, 168050.40, 'buy', '2026-05-27', 1, 0, 0);

-- 宁德时代：买入后全部卖出（已清仓）
INSERT INTO fnos_trades (buy_order_no, contract, name, price, shares, remaining_shares, amount, fee, net_amount, trade_type, trade_date, user_id, realized_profit, single_profit) VALUES
('T20260530001', '300750', '宁德时代', 218.50, 200, 0, 43700.00, 13.11, 43713.11, 'buy', '2026-05-30', 1, 0, 0),
('T20260530001', '300750', '宁德时代', 225.80, 200, 0, 45160.00, 13.55, 45146.45, 'sell', '2026-05-31', 1, 1433.34, 1433.34);

-- 招商银行：1笔买入
INSERT INTO fnos_trades (buy_order_no, contract, name, price, shares, remaining_shares, amount, fee, net_amount, trade_type, trade_date, user_id, realized_profit, single_profit) VALUES
('T20260601001', '600036', '招商银行', 38.20, 1000, 1000, 38200.00, 11.46, 38211.46, 'buy', '2026-06-01', 1, 0, 0);

-- 比亚迪：1笔买入
INSERT INTO fnos_trades (buy_order_no, contract, name, price, shares, remaining_shares, amount, fee, net_amount, trade_type, trade_date, user_id, realized_profit, single_profit) VALUES
('T20260602001', '002594', '比亚迪', 285.00, 100, 100, 28500.00, 8.55, 28508.55, 'buy', '2026-06-02', 1, 0, 0);

-- ============================================
-- 持仓数据 (user_id=1)
-- ============================================
INSERT INTO fnos_positions (contract, name, user_id, total_shares, avg_cost, latest_price, market_value, profit, profit_rate) VALUES
('601318', '中国平安', 1, 600, 52.08, 55.20, 33120.00, 1870.00, 5.98),
('600519', '贵州茅台', 1, 100, 1680.50, 1720.00, 172000.00, 3950.00, 2.35),
('600036', '招商银行', 1, 1000, 38.21, 37.80, 37800.00, -411.46, -1.08),
('002594', '比亚迪', 1, 100, 285.09, 290.50, 29050.00, 541.45, 1.90);
