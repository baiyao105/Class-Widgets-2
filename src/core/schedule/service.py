from datetime import datetime, timedelta
from typing import Optional, List

from src.core.models.schedule import Entry, EntryType, DayEntry, Subject, ScheduleData


class ScheduleServices:

    @staticmethod
    def get_day_entries(schedule: ScheduleData, now: datetime) -> DayEntry | None:
        weekday = now.isoweekday()  # 1-7
        for day in schedule.days:
            if day.dayOfWeek == weekday:
                return day
        return None

    @staticmethod
    def get_current_entry(day: DayEntry, now: Optional[datetime] = None) -> Optional[Entry]:
        now = now or datetime.now()
        time = now.time()
        for entry in day.entries:
            try:
                start = datetime.strptime(entry.startTime, "%H:%M").time()
                end = datetime.strptime(entry.endTime, "%H:%M").time()
            except ValueError:
                continue
            if start <= time < end:
                return entry
        return None

    @staticmethod
    def get_next_entries(day: DayEntry, now: Optional[datetime] = None) -> List[Entry]:
        now = now or datetime.now()
        now_time = now.time()
        next_entries = [
            e for e in day.entries
            if datetime.strptime(e.startTime, "%H:%M").time() > now_time
            and e.type in {EntryType.CLASS, EntryType.ACTIVITY}
        ]
        return sorted(next_entries, key=lambda e: datetime.strptime(e.startTime, "%H:%M").time())

    @staticmethod
    def get_remaining_time(day: DayEntry, now: Optional[datetime] = None) -> timedelta:
        now = now or datetime.now()
        current = ScheduleServices.get_current_entry(day, now)
        if current:
            end_time = datetime.strptime(current.endTime, "%H:%M").time()
            end_dt = now.replace(hour=end_time.hour, minute=end_time.minute, second=0, microsecond=0)
            return max(end_dt - now, timedelta(0))
        upcoming = ScheduleServices.get_next_entries(day, now)
        if upcoming:
            next_start = datetime.strptime(upcoming[0].startTime, "%H:%M").time()
            next_dt = now.replace(hour=next_start.hour, minute=next_start.minute, second=0, microsecond=0)
            return max(next_dt - now, timedelta(0))
        return timedelta(0)

    @staticmethod
    def get_current_status(day: DayEntry, now: Optional[datetime] = None) -> EntryType:
        return ScheduleServices.get_current_entry(day, now).type if ScheduleServices.get_current_entry(day, now) else EntryType.FREE

    @staticmethod
    def get_current_subject(day: DayEntry, subjects: List[Subject], now: Optional[datetime] = None) -> Optional[Subject]:
        current = ScheduleServices.get_current_entry(day, now)
        if current and current.subjectId:
            for s in subjects:
                if s.id == current.subjectId:
                    return s
        return None
