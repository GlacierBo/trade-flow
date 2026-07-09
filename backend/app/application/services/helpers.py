"""共享辅助函数"""


def to_float(val) -> float | None:
    """将 Decimal / str / int / None 安全转为 float 或 None"""
    return float(val) if val is not None else None
