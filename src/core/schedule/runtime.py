from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Optional, List

from PySide6.QtCore import QObject, Property, Signal
from loguru import logger

from src.core.models.schedule import ScheduleData, MetaInfo, DayEntry, Entry, EntryType, Subject
from src.core.schedule.service import ScheduleServices
from src.core.utils import get_cycle_week, get_week_number


class ScheduleRuntime(QObject):
    notify = Signal(str, dict, str)
    updated = Signal()

    def __init__(self, schedule: ScheduleData, app_central):
        super().__init__()
        self.app_central = app_central
        self.schedule = schedule
        self.current_time = datetime.now()

        self.current_day_of_week: int = 0
        self.current_week = 0
        self.current_week_of_cycle: int = 0

        self.schedule_meta: Optional[MetaInfo] = None
        self.current_day: Optional[DayEntry] = None
        self.previous_entry: Optional[Entry] = None
        self.current_entry: Optional[Entry] = None
        self.next_entries: Optional[List[Entry]] = None
        self.remaining_time: Optional[timedelta] = None
        self._progress: Optional[float] = None
        self.current_status: Optional[EntryType] = None

        self.current_subject: Optional[Subject] = None
        self.current_title: Optional[str] = None

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
    @Property(list, notify=updated)
    def subjects(self) -> list:
        return [s.model_dump() for s in self.schedule.subjects]

    @Property(dict, notify=updated)
    def scheduleMeta(self) -> dict:
        if self.schedule_meta is None:
            return {}
        return self.schedule_meta.model_dump()

    @Property(list, notify=updated)
    def currentDayEntries(self) -> list:  # 当前的日程
        if not self.current_day:
            return []
        return [entry.model_dump() for entry in self.current_day.entries]

    @Property(dict, notify=updated)
    def currentEntry(self) -> dict:
        return self.current_entry.model_dump() if self.current_entry else {}

    @Property(list, notify=updated)
    def nextEntries(self) -> list:  # 接下来的日程
        if not self.next_entries:
            return []
        return [entry.model_dump() for entry in self.next_entries]

    @Property(dict, notify=updated)
    def remainingTime(self) -> dict:
        if not self.remaining_time:
            return {
                "minute": 0,
                "second": 0
            }
        result = {
            "minute": self.remaining_time.seconds // 60,
            "second": self.remaining_time.seconds % 60
        }
        return result

    @Property(float, notify=updated)
    def progress(self) -> float:
        if not self._progress:
            return 0.0
        return self._progress

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
        self.schedule = schedule or self.schedule
        self.schedule_meta = self.schedule.meta
        self.current_day = ScheduleServices.get_day_entries(self.schedule, self.current_time)

        if self.current_day:
            self.current_entry = ScheduleServices.get_current_entry(self.current_day, self.current_time)
            self.next_entries = ScheduleServices.get_next_entries(self.current_day, self.current_time)
            self.remaining_time = ScheduleServices.get_remaining_time(self.current_day, self.current_time)
            self.current_status = ScheduleServices.get_current_status(self.current_day, self.current_time)
            self.current_subject = ScheduleServices.get_current_subject(self.current_day, self.schedule.subjects, self.current_time)
            self.current_title = getattr(self.current_entry, "title", None)

        self._progress = self.get_progress_percent()

    def _update_time(self):  # 更新时间
        self.current_day_of_week = self.current_time.isoweekday()
        self.current_week = get_week_number(self.schedule.meta.startDate, self.current_time)
        self.current_week_of_cycle = get_cycle_week(self.current_week, self.schedule.meta.maxWeekCycle)

    def get_progress_percent(self) -> float:
        if not self.current_entry:  # 空
            return 1

        now = self.current_time
        start = datetime.combine(now.date(), datetime.strptime(self.current_entry.startTime, "%H:%M").time())
        end = datetime.combine(now.date(), datetime.strptime(self.current_entry.endTime, "%H:%M").time())

        if now <= start: return 0
        if now >= end: return 1
        return round((now - start).total_seconds() / (end - start).total_seconds(), 2)

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
            prep_min = self.app_central.configs.schedule.preparation_time or 2  # 准备时间
            # prep_min = self.app_central.configs.get("schedule").get("preparation_time") or 2  # 准备时间

            if next_start - timedelta(minutes=prep_min) == self.current_time.replace(microsecond=0):  # 调整当前精度……
                logger.info(f"Notify: status changed to {EntryType.PREPARATION.value}; {next_entry}")
                self.notify.emit(
                    EntryType.PREPARATION.value,
                    asdict(next_entry.get_subject(self.schedule.subjects) if self.schedule.subjects else None),
                    next_entry.title if next_entry else None
                )
