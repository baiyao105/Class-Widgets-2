from datetime import datetime


def get_week_number(start_date: str, current_date: datetime) -> int:
    """获取第几周（从1开始）"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    delta_days = (current_date.date() - start.date()).days
    return delta_days // 7 + 1


def get_cycle_week(week_number: int, cycle: int) -> int:
    """获取在 max_week_cycle 中是第几周（从1开始）"""
    return ((week_number - 1) % cycle) + 1
