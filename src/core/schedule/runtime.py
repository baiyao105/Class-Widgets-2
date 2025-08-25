from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Optional, List

from PySide6.QtCore import QObject, Property, Signal
from loguru import logger

from src.core.models import DayEntry, Entry, MetaInfo, EntryType, Subject
from src.core.models import ScheduleData
from src.core.utils import get_cycle_week, get_week_number


class ScheduleRuntime(QObject):
    notify = Signal(str, dict, str)  # entry_type, subject, title
    updated = Signal()

    def __init__(self, schedule: ScheduleData, app_central):
        super().__init__()
        self.app_central = app_central
        self.schedule = schedule
        self.current_time = datetime.now()

        # TIME
        self.current_day_of_week: int = 0  # 当前星期
        self.current_week = 0  # 当前周
        self.current_week_of_cycle: int = 0  # 当前周的周期

        # SCHEDULE
        self.schedule_meta: Optional[MetaInfo] = None  # 日程元数据
        self.current_day: Optional[DayEntry] = None  # 当前天的所有日程
        self.previous_entry: Optional[Entry] = None  # 上一个日程(检测日程变更)
        self.current_entry: Optional[Entry] = None  # 当前正在进行的日程
        self.next_entries: Optional[List[Entry]] = None  # 接下来的日程
        self.remaining_time: Optional[timedelta] = None  # 剩余时间
        self.current_status: Optional[EntryType] = None  # 当前状态

        # SUBJECT
        self.current_subject: Optional[Subject] = None  # 当前科目
        self.current_title: Optional[str] = None  # 当前标题

        logger.info("Schedule runtime initialized.")

    # TIME
    @Property(str, notify=updated)
    def currentTime(self) -> str:
        return self.current_time.strftime("%H:%M:%S")

    @Property(int, notify=updated)
    def currentDayOfWeek(self) -> int:
        return self.current_day_of_week

    @Property(dict, notify=updated)
    def currentDate(self) -> dict:
        return { "year": self.current_time.year, "month": self.current_time.month, "day": self.current_time.day }

    @Property(int, notify=updated)
    def currentWeek(self) -> int:
        return self.current_week

    @Property(int, notify=updated)
    def currentWeekOfCycle(self) -> int:
        return self.current_week_of_cycle

    # SCHEDULE
    @Property(dict, notify=updated)
    def scheduleMeta(self) -> dict:
        return asdict(self.schedule_meta)

    @Property(list, notify=updated)
    def currentDayEntries(self) -> list:  # 当前的进行的日程
        result = []
        if not self.current_day:
            return result
        for i in range(len(self.current_day.entries)):
            result.append(asdict(self.current_day.entries[i]))
        return result

    @Property(dict, notify=updated)
    def currentEntry(self) -> dict:
        return asdict(self.current_entry) if self.current_entry else None

    @Property(list, notify=updated)
    def nextEntries(self) -> list:  # 接下来的日程
        converted = []
        if not self.next_entries:
            return converted
        for i in range(len(self.next_entries)):
            converted.append(asdict(self.next_entries[i]))
        return converted

    @Property(dict, notify=updated)
    def remainingTime(self) -> dict:
        if not self.remaining_time:
            return {
                "minutes": 0,
                "seconds": 0
            }
        result = {
            "minutes": self.remaining_time.seconds // 60,
            "seconds": self.remaining_time.seconds % 60
        }
        return result

    @Property(str, notify=updated)
    def currentStatus(self):
        if not self.current_status:
            return EntryType.FREE.value
        return self.current_status.value

    # SUBJECT
    @Property(dict, notify=updated)
    def currentSubject(self) -> dict:
        return asdict(self.current_subject) if self.current_subject else None

    @Property(str, notify=updated)
    def currentTitle(self) -> str:
        return self.current_title

    def update(self, schedule: ScheduleData = None):
        self._update_schedule(schedule)
        self._update_time()
        self._update_notify()
        self.updated.emit()

    def _update_schedule(self, schedule: ScheduleData):
        """
        更新日程
        :param schedule:
        :return:
        """
        self.current_time = datetime.now()

        self.schedule = schedule
        self.schedule_meta = self.schedule.meta
        self.current_day = self.schedule.get_day_entries(self.current_time)
        self.current_entry = self.current_day.get_current_entry(self.current_time) if self.current_day else None
        self.next_entries = self.current_day.get_next_entries(self.current_time) if self.current_day else None
        self.remaining_time = self.current_day.get_remaining_time(self.current_time) if self.current_day else None
        self.current_status = self.current_day.get_current_status(self.current_time) if self.current_day else None
        self.current_subject = self.current_day.get_current_subject(self.schedule.subjects, self.current_time) if self.current_day else None
        self.current_title = getattr(self.current_entry, "title", None)

    def _update_time(self):  # 更新时间
        self.current_day_of_week = self.current_time.isoweekday()
        self.current_week = get_week_number(self.schedule.meta.startDate, self.current_time)
        self.current_week_of_cycle = get_cycle_week(self.current_week, self.schedule.meta.maxWeekCycle)

    def _update_notify(self):
        # 活动变更节点
        if self.previous_entry != self.current_entry:
            self.previous_entry = self.current_entry
            logger.info(f"Notify: status changed to {self.current_status.value}; {self.previous_entry}")
            self.notify.emit(self.current_status.value, self.current_subject, self.current_title)

        # 预备铃
        if (
            self.next_entries and len(self.next_entries) > 0 and
            self.current_status in {EntryType.FREE, EntryType.PREPARATION}
        ):
            next_entry = self.next_entries[0]
            next_start = datetime.strptime(next_entry.startTime, "%H:%M")
            next_start = datetime.combine(self.current_time.date(), next_start.time())
            prep_min = self.app_central.configs.preferences.preparation_time or 2  # 准备时间
            # prep_min = self.app_central.configs.get("schedule").get("preparation_time") or 2  # 准备时间

            if next_start - timedelta(minutes=prep_min) == self.current_time.replace(microsecond=0):  # 调整当前精度……
                logger.info(f"Notify: status changed to {EntryType.PREPARATION.value}; {next_entry}")
                self.notify.emit(
                    EntryType.PREPARATION.value,
                    asdict(next_entry.get_subject(self.schedule.subjects) if self.schedule.subjects else None),
                    next_entry.title if next_entry else None
                )
