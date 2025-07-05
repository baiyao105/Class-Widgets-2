from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List, Union
from enum import Enum

from src.core.utils import get_week_number, get_cycle_week


# 枚举类
class EntryType(str, Enum):
    CLASS = "class"
    BREAK = "break"
    ACTIVITY = "activity"
    FREE = "free"


# 科目
@dataclass
class Subject:
    id: str
    name: str
    teacher: Optional[str] = None
    icon: Optional[str] = None
    location: Optional[str] = None
    is_local_classroom: bool = True


# 活动条目
@dataclass
class Entry:
    id: str
    type: EntryType
    start_time: str
    end_time: str
    subject_id: Optional[str] = None  # 当类型为 activity 时，指定 subject_id
    title: Optional[str] = None  # break / activity 用，可覆盖 subject


# 天
@dataclass
class DayEntry:
    id: str
    entries: List[Entry]

    # 以下二选一：
    day_of_week: Optional[int] = 1  # 1~7 表示星期一到星期日
    weeks: Union[str, List[int], None] = None  # str "all"（暂时只想得到这个） 或 list [1, 2, 3]（第x到x周） 或 [1] 表示每x周

    date: Optional[str] = None  # 指定具体日期，如 "2026-09-01"

    def get_current_entry(self, date: Optional[datetime] = None) -> Optional[Entry]:
        """
        获取当前时间段的活动条目
        :param date:
        :return:
        """
        date = date or datetime.now()
        time = date.time()

        for entry in self.entries:
            try:
                start = datetime.strptime(entry.start_time, "%H:%M").time()
                end = datetime.strptime(entry.end_time, "%H:%M").time()
            except ValueError:
                continue  # 忽略无效时间格式
            if start <= time < end:
                return entry

        return None

    def get_next_entries(self, now: Optional[datetime] = None) -> List[Entry]:
        """
        获取当日接下来的日程
        :param now:
        :return:
        """
        now = now or datetime.now()
        now_time = now.time()

        next_entries = [
            entry for entry in self.entries
            if datetime.strptime(entry.start_time, "%H:%M").time() > now_time
        ]

        return sorted(next_entries, key=lambda e: e.start_time)

    def get_remaining_time(self, now: Optional[datetime] = None) -> timedelta:
        """
        获取剩余时间/活动开始倒计时
        :param now:
        :return:
        """
        now = now or datetime.now()
        current = self.get_current_entry(now)

        if current:  # 当前活动倒计时
            end_time = datetime.strptime(current.end_time, "%H:%M").time()
            end_dt = now.replace(hour=end_time.hour, minute=end_time.minute, second=0, microsecond=0)
            return max(end_dt - now, timedelta(0))
        upcoming = self.get_next_entries(now)
        if upcoming:  # 下一活动开始
            next_start = datetime.strptime(upcoming[0].start_time, "%H:%M").time()
            next_dt = now.replace(hour=next_start.hour, minute=next_start.minute, second=0, microsecond=0)
            return max(next_dt - now, timedelta(0))

        return timedelta(0)

    def get_current_status(self, now: Optional[datetime] = None) -> Optional[EntryType]:
        """
        获取当前状态
        :param now:
        :return:
        """
        now = now or datetime.now()
        current = self.get_current_entry(now)
        if current:
            return current.type
        return EntryType.FREE

    def get_current_subject(self, subjects: List[Subject], now: Optional[datetime] = None) -> Optional[Subject]:
        """
        获取当前正在进行的课程对应的 Subject
        :param subjects:
        :param now: 当前时间
        :return: 匹配到的 Subject 或 None
        """
        now = now or datetime.now()
        current = self.get_current_entry(now)

        if not current:
            return None
        if current.type in {EntryType.CLASS, EntryType.ACTIVITY} and current.subject_id:
            for subject in subjects:
                if subject.id == current.subject_id:
                    return subject
        return None


# 元信息
@dataclass
class MetaInfo:
    id: str
    version: int
    max_week_cycle: int
    start_date: str  # like"2026-09-01"


# 总框架
@dataclass
class ScheduleData:
    meta: MetaInfo
    subjects: List[Subject]
    days: List[DayEntry]

    def get_day_entries(self, date: Optional[datetime] = None) -> Optional[DayEntry]:
        """
        根据日期获取当天日程
        :param date:
        :return:
        """
        date = date or datetime.now()
        date_str = date.strftime("%Y-%m-%d")
        weekday = date.isoweekday()
        week_number = get_week_number(self.meta.start_date, date)
        cycle_week = get_cycle_week(week_number, self.meta.max_week_cycle)

        # 优先匹配 date 字段
        for day in self.days:
            if day.date == date_str:
                return day

        # 没有则匹配星期
        for day in self.days:
            if day.day_of_week != weekday:
                continue
            if day.weeks is None or day.weeks == "all":
                return day
            if isinstance(day.weeks, list) and cycle_week in day.weeks:
                return day
        return None
