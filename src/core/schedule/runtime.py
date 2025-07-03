from datetime import datetime
from typing import Optional, List

from PySide6.QtCore import QObject, Slot, Property, Signal
from loguru import logger

from src.core.models import DayEntry, Entry
from src.core.models import ScheduleData
from src.core.utils import to_dict


class ScheduleRuntime(QObject):
    updated = Signal()

    def __init__(self, schedule: ScheduleData):
        super().__init__()
        self.schedule = schedule
        self.current_time: datetime = datetime.now()

        self.current_day_of_week: int = 0  # 当前星期
        self.current_day: Optional[DayEntry] = None  # 当前天的所有日程
        self.current_entry: Optional[Entry] = None  # 当前正在进行的日程
        self.next_entries: Optional[List[Entry]] = None  # 接下来的日程

        logger.info("Schedule runtime initialized.")

    @Property(str, notify=updated)
    def currentTime(self) -> str:
        return self.current_time.strftime("%H:%M:%S")

    @Property(int, notify=updated)
    def currentDayOfWeek(self) -> int:
        return self.current_day_of_week

    @Property(dict, notify=updated)
    def currentDate(self) -> dict:
        return { "year": self.current_time.year, "month": self.current_time.month, "day": self.current_time.day }

    @Property(list, notify=updated)
    def currentDayEntries(self) -> list:  # 当前的进行的日程
        return self.current_day.entries if self.current_day else []

    @Property(dict, notify=updated)
    def currentEntry(self) -> dict:
        return to_dict(self.current_entry) if self.current_entry else None

    @Property(list, notify=updated)
    def nextEntries(self) -> list:  # 接下来的日程
        converted = []
        for i in range(len(self.next_entries)):
            converted.append(to_dict(self.next_entries[i]))
        return converted

    def update(self, schedule: ScheduleData = None):
        self._update_time()
        self._update_schedule(schedule)
        self.updated.emit()

    def _update_schedule(self, schedule: ScheduleData):
        """
        更新日程
        :param schedule:
        :return:
        """
        self.schedule = schedule
        self.current_day = self.schedule.get_day_entries(self.current_time)
        self.current_entry = self.current_day.get_current_entry(self.current_time)
        self.next_entries = self.current_day.get_next_entries(self.current_time)

    def _update_time(self):  # 更新时间
        self.current_time = datetime.now()
        self.current_day_of_week = self.current_time.isoweekday()

    # For QML
    # @Slot(result=int)
    # def get_current_time(self) -> datetime:
    #     return int(self.current_time.timestamp())
