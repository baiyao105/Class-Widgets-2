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
    PREPARATION = "preparation"


class WeekType(str, Enum):
    ALL = "all"


# FUNCTIONS
def is_week_matched(week: int, cycle_week: int, weeks: Union[WeekType, List[int], int, None]) -> bool:
    if weeks is None:
        return False
    if weeks == WeekType.ALL:
        return True
    if isinstance(weeks, list):
        return week in weeks
    if isinstance(weeks, int):
        return weeks == cycle_week
    return False


# 科目
@dataclass
class Subject:
    id: str
    name: str
    teacher: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None  # 16进制颜色值，如 "#FF0000"(byd差点忘了)
    location: Optional[str] = None
    isLocalClassroom: bool = True


# 活动条目
@dataclass
class Entry:
    id: str
    type: EntryType
    startTime: str
    endTime: str
    subjectId: Optional[str] = None  # 当类型为 activity 时，指定 subject_id
    title: Optional[str] = None  # break / activity 用，可覆盖 subject

    def get_subject(self, subjects: List[Subject]) -> Optional[Subject]:
        """
        获取当前活动对应的 Subject
        :return:
        """
        if self.type in {EntryType.CLASS, EntryType.ACTIVITY} and self.subjectId:
            for subject in subjects:
                if subject.id == self.subjectId:
                    return subject
        return None


# 天
@dataclass
class DayEntry:
    id: str
    entries: List[Entry]

    # 以下二选一：
    dayOfWeek: Optional[int] = 1  # 1~7 表示星期一到星期日
    weeks: Union[WeekType, str, List[int], int, None] = None  # WeekType:ALL（暂时只想得到这个） 或 list:[1, 2, 3]（第x到x周） 或 int:1 表示每x周

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
                start = datetime.strptime(entry.startTime, "%H:%M").time()
                end = datetime.strptime(entry.endTime, "%H:%M").time()
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
            if datetime.strptime(entry.startTime, "%H:%M").time() > now_time
        ]

        return sorted(next_entries, key=lambda e: datetime.strptime(e.startTime, "%H:%M").time())

    def get_remaining_time(self, now: Optional[datetime] = None) -> timedelta:
        """
        获取剩余时间/活动开始倒计时
        :param now:
        :return:
        """
        now = now or datetime.now()
        current = self.get_current_entry(now)

        if current:  # 当前活动倒计时
            end_time = datetime.strptime(current.endTime, "%H:%M").time()
            end_dt = now.replace(hour=end_time.hour, minute=end_time.minute, second=0, microsecond=0)
            return max(end_dt - now, timedelta(0))
        upcoming = self.get_next_entries(now)
        if upcoming:  # 下一活动开始
            next_start = datetime.strptime(upcoming[0].startTime, "%H:%M").time()
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
        if current.type in {EntryType.CLASS, EntryType.ACTIVITY} and current.subjectId:
            for subject in subjects:
                if subject.id == current.subjectId:
                    return subject
        return None


# 元信息
@dataclass
class MetaInfo:
    id: str
    version: int
    maxWeekCycle: int
    startDate: str  # like"2026-09-01"


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
        week_number = get_week_number(self.meta.startDate, date)
        cycle_week = get_cycle_week(week_number, self.meta.maxWeekCycle)

        # 优先匹配具体日期
        for day in self.days:
            if day.date == date_str:
                return day

        # 其次匹配星期和周期条件
        for day in self.days:
            if day.dayOfWeek != weekday:
                continue
            if is_week_matched(week_number, cycle_week, day.weeks):
                return day

        return None
