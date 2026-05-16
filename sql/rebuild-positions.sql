-- 重建所有持仓记录（从现有交易数据重新计算）
-- 修改 recalculate_position 函数后运行此脚本，恢复已平仓的持仓记录

SELECT recalculate_position(contract) FROM (
    SELECT DISTINCT contract FROM stock_trades
) sub;
