"""
修复数据库中 Unicode 转义序列乱码问题

将 fnos_watchlist.name 和 fnos_stocks.name 中存储的
    医疗ETF华宝  (纯文本)
修复为
    医疗ETF华宝                   (实际中文字符)

使用方法:
    cd backend
    python fix_unicode_data.py
"""
import re
import sys
from pathlib import Path

# 确保能找到 app 模块
sys.path.insert(0, str(Path(__file__).parent))

from app.infrastructure.database import SessionLocal


def unescape_text(text: str) -> str:
    """将字符串中的 \\uXXXX 转义序列转换为实际 Unicode 字符"""
    def replace_match(m):
        return chr(int(m.group(1), 16))
    return re.sub(r'\\u([0-9a-fA-F]{4})', replace_match, text)


def has_unicode_escapes(text: str) -> bool:
    """检查是否包含 \\uXXXX 模式的转义序列"""
    return bool(re.search(r'\\u[0-9a-fA-F]{4}', text))


def fix_watchlist(db) -> int:
    """修复 fnos_watchlist 表中的 name 字段"""
    from app.domain.models import Watchlist

    items = db.query(Watchlist).all()
    fixed_count = 0

    for item in items:
        if item.name and has_unicode_escapes(item.name):
            original = item.name
            decoded = unescape_text(item.name)
            item.name = decoded
            fixed_count += 1
            print(f"  [watchlist] {item.code}: {original[:40]}... → {decoded}")

    if fixed_count > 0:
        db.commit()

    return fixed_count


def fix_stocks(db) -> int:
    """修复 fnos_stocks 表中的 name 字段"""
    from app.domain.models import Stock

    items = db.query(Stock).all()
    fixed_count = 0

    for item in items:
        if item.name and has_unicode_escapes(item.name):
            original = item.name
            decoded = unescape_text(item.name)
            item.name = decoded
            fixed_count += 1
            print(f"  [stocks] {item.code}: {original[:40]}... → {decoded}")

    if fixed_count > 0:
        db.commit()

    return fixed_count


def fix_trades(db) -> int:
    """修复 fnos_trades 表中的 name 字段"""
    from app.domain.models import Trade

    items = db.query(Trade).all()
    fixed_count = 0

    for item in items:
        if item.name and has_unicode_escapes(item.name):
            original = item.name
            decoded = unescape_text(item.name)
            item.name = decoded
            fixed_count += 1
            print(f"  [trades] {item.contract}: {original[:40]}... → {decoded}")

    if fixed_count > 0:
        db.commit()

    return fixed_count


def fix_positions(db) -> int:
    """修复 fnos_positions 表中的 name 字段"""
    from app.domain.models import Position

    items = db.query(Position).all()
    fixed_count = 0

    for item in items:
        if item.name and has_unicode_escapes(item.name):
            original = item.name
            decoded = unescape_text(item.name)
            item.name = decoded
            fixed_count += 1
            print(f"  [positions] {item.contract}: {original[:40]}... → {decoded}")

    if fixed_count > 0:
        db.commit()

    return fixed_count


def main():
    print("=" * 60)
    print("Unicode 转义序列修复脚本")
    print("=" * 60)

    # 列出受影响的表
    tables_to_check = [
        ("自选股 (fnos_watchlist)", fix_watchlist),
        ("股票行情 (fnos_stocks)", fix_stocks),
        ("交易记录 (fnos_trades)", fix_trades),
        ("持仓 (fnos_positions)", fix_positions),
    ]

    total = 0

    for name, fix_func in tables_to_check:
        print(f"\n检查 {name}...")
        db = SessionLocal()
        try:
            count = fix_func(db)
            if count > 0:
                print(f"  ✅ 修复了 {count} 条记录")
            else:
                print(f"  ✅ 无需要修复的记录")
            total += count
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        finally:
            db.close()

    print(f"\n{'=' * 60}")
    if total > 0:
        print(f"🎉 共修复 {total} 条记录")
        print("请刷新前端页面查看效果")
    else:
        print("✅ 所有数据都已正确编码，无需修复")

    print(f"\n提示：如果这是通过容器运行的，请执行:")
    print(f"  docker cp fix_unicode_data.py <容器名>:/app/backend/")
    print(f"  docker exec <容器名> python /app/backend/fix_unicode_data.py")


if __name__ == "__main__":
    main()
