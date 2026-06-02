"""生成测试数据"""
import sys
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import text

from app.database import SessionLocal, engine
from app.models.trade import Trade
from app.models.position import Position
from app.models.serial_counter import SerialCounter


def seed():
    db = SessionLocal()
    try:
        # 清空旧数据
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        db.execute(text("TRUNCATE TABLE fnos_trades"))
        db.execute(text("TRUNCATE TABLE fnos_positions"))
        db.execute(text("TRUNCATE TABLE fnos_serial_counters"))
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        db.commit()

        today = date.today()

        # ========== 流水号计数器 ==========
        counters = [
            SerialCounter(counter_date=(today - timedelta(days=i)).strftime("%Y%m%d"), current_serial=3)
            for i in range(5)
        ]
        db.add_all(counters)

        # ========== 交易数据 ==========
        # 模拟网格交易：同一合约多次买入，分批卖出
        trades_data = [
            # --- 中国平安 601318 ---
            # 第1笔买入
            {"buy_order_no": "T20260528001", "contract": "601318", "name": "中国平安",
             "price": 52.30, "shares": 500, "remaining_shares": 200, "amount": 26150.00,
             "fee": 7.85, "net_amount": 26157.85, "trade_type": "buy", "trade_date": today - timedelta(days=5),
             "user_id": 1},
            # 第1笔部分卖出
            {"buy_order_no": "T20260528001", "contract": "601318", "name": "中国平安",
             "price": 54.80, "shares": 300, "remaining_shares": 0, "amount": 16440.00,
             "fee": 4.93, "net_amount": 16435.07, "trade_type": "sell", "trade_date": today - timedelta(days=3),
             "user_id": 1, "realized_profit": 737.22, "single_profit": 737.22},
            # 第2笔买入
            {"buy_order_no": "T20260529001", "contract": "601318", "name": "中国平安",
             "price": 51.50, "shares": 400, "remaining_shares": 400, "amount": 20600.00,
             "fee": 6.18, "net_amount": 20606.18, "trade_type": "buy", "trade_date": today - timedelta(days=4),
             "user_id": 1},

            # --- 贵州茅台 600519 ---
            {"buy_order_no": "T20260527001", "contract": "600519", "name": "贵州茅台",
             "price": 1680.00, "shares": 100, "remaining_shares": 100, "amount": 168000.00,
             "fee": 50.40, "net_amount": 168050.40, "trade_type": "buy", "trade_date": today - timedelta(days=6),
             "user_id": 1},

            # --- 宁德时代 300750 ---
            # 买入
            {"buy_order_no": "T20260530001", "contract": "300750", "name": "宁德时代",
             "price": 218.50, "shares": 200, "remaining_shares": 0, "amount": 43700.00,
             "fee": 13.11, "net_amount": 43713.11, "trade_type": "buy", "trade_date": today - timedelta(days=2),
             "user_id": 1},
            # 全部卖出（盈利）
            {"buy_order_no": "T20260530001", "contract": "300750", "name": "宁德时代",
             "price": 225.80, "shares": 200, "remaining_shares": 0, "amount": 45160.00,
             "fee": 13.55, "net_amount": 45146.45, "trade_type": "sell", "trade_date": today - timedelta(days=1),
             "user_id": 1, "realized_profit": 1433.34, "single_profit": 1433.34},

            # --- 招商银行 600036 ---
            {"buy_order_no": "T20260601001", "contract": "600036", "name": "招商银行",
             "price": 38.20, "shares": 1000, "remaining_shares": 1000, "amount": 38200.00,
             "fee": 11.46, "net_amount": 38211.46, "trade_type": "buy", "trade_date": today - timedelta(days=1),
             "user_id": 1},

            # --- 比亚迪 002594 ---
            {"buy_order_no": "T20260602001", "contract": "002594", "name": "比亚迪",
             "price": 285.00, "shares": 100, "remaining_shares": 100, "amount": 28500.00,
             "fee": 8.55, "net_amount": 28508.55, "trade_type": "buy", "trade_date": today,
             "user_id": 1},
        ]

        for td in trades_data:
            db.add(Trade(**td))

        # ========== 持仓数据 ==========
        positions_data = [
            {"contract": "601318", "name": "中国平安", "user_id": 1,
             "total_shares": 600, "avg_cost": 52.08, "latest_price": 55.20,
             "market_value": 33120.00, "profit": 1870.00, "profit_rate": 5.98},
            {"contract": "600519", "name": "贵州茅台", "user_id": 1,
             "total_shares": 100, "avg_cost": 1680.50, "latest_price": 1720.00,
             "market_value": 172000.00, "profit": 3950.00, "profit_rate": 2.35},
            {"contract": "600036", "name": "招商银行", "user_id": 1,
             "total_shares": 1000, "avg_cost": 38.21, "latest_price": 37.80,
             "market_value": 37800.00, "profit": -411.46, "profit_rate": -1.08},
            {"contract": "002594", "name": "比亚迪", "user_id": 1,
             "total_shares": 100, "avg_cost": 285.09, "latest_price": 290.50,
             "market_value": 29050.00, "profit": 541.45, "profit_rate": 1.90},
        ]

        for pd in positions_data:
            db.add(Position(**pd))

        db.commit()
        print("[OK] 测试数据生成成功!")
        print(f"   - 流水号计数器: {len(counters)} 条")
        print(f"   - 交易记录: {len(trades_data)} 条")
        print(f"   - 持仓数据: {len(positions_data)} 条")

    except Exception as e:
        db.rollback()
        print(f"[FAIL] 生成失败: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
