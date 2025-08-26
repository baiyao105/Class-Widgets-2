import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

from PySide6.QtCore import QObject, Property, Signal, Slot
from loguru import logger

from src.core.models import ScheduleData, Subject, DayEntry, Entry, MetaInfo, EntryType
from src.core.models.schedule import WeekType
from src.core.parser import ScheduleParser
from src.core.utils import generate_id


class ScheduleEditor(QObject):
    updated = Signal()

    def __init__(self, schedule_path: Union[Path, str]):
        super().__init__()
        self.schedule_path = Path(schedule_path)
        self.parser = ScheduleParser(self.schedule_path)
        self.schedule: Optional[ScheduleData] = None
        self._load_schedule()

    def set_schedule_path(self, schedule_path: Union[Path, str]) -> None:
        self.schedule_path = Path(schedule_path)
        self.parser = ScheduleParser(self.schedule_path)
        self._load_schedule()

    def _load_schedule(self) -> None:
        """加载课程表"""
        try:
            self.schedule = self.parser.load()
        except FileNotFoundError:
            logger.warning("Schedule file not found, creating a new one...")
            self._create_empty_schedule()
        except Exception as e:
            logger.error(f"Load schedule failed: {e}")
            raise

    def _create_empty_schedule(self) -> None:
        """创建空的课程表"""
        self.schedule = ScheduleData(
            meta=MetaInfo(
                id=generate_id("meta"),
                version=1,  
                maxWeekCycle=2,
                startDate="2026-09-01"
            ),
            subjects=[],
            days=[]
        )
        self.save()

    @Slot()
    def save(self) -> None:
        """保存课程表到文件"""
        if not self.schedule:
            return
        
        schedule_dict = asdict(self.schedule)

        try:
            with open(self.schedule_path, "w", encoding="utf-8") as f:
                json.dump(schedule_dict, f, ensure_ascii=False, indent=4)
            logger.info(f"Schedule saved to {self.schedule_path}")
        except Exception as e:
            logger.error(f"Save schedule failed: {e}")
        self.updated.emit()

    # Subject 操作
    @Slot(str, str, str, str, str, bool, result=str)
    def addSubject(self, name: str, teacher: str = "", icon: str = "", color: str = "",
                   location: str = "", is_local_classroom: bool = True) -> str:
        """添加科目"""
        subject = Subject(
            id=generate_id("subj"),
            name=name,
            teacher=teacher or None,
            icon=icon or None,
            color=color or None,
            location=location or None,
            isLocalClassroom=is_local_classroom
        )
        self.schedule.subjects.append(subject)
        self.save()
        return subject.id

    @Slot(str, str, str, str, str, str, bool)
    def updateSubject(self, subject_id: str, name: str = "", teacher: str = "",
                      icon: str = "", color: str = "", location: str = "", is_local_classroom: bool = True) -> None:
        """更新科目"""
        subject = self.getSubject(subject_id)
        if not subject:
            return

        if name:
            subject.name = name
        if teacher:
            subject.teacher = teacher
        if icon:
            subject.icon = icon
        if color:
            subject.color = color
        if location:
            subject.location = location
        subject.isLocalClassroom = is_local_classroom

    @Slot(str)
    def removeSubject(self, subject_id: str) -> None:
        """删除科目"""
        subject = self.getSubject(subject_id)
        if not subject:
            return

        # 删除相关的课程条目
        for day in self.schedule.days:
            day.entries = [e for e in day.entries if e.subject_id != subject_id]

        self.schedule.subjects.remove(subject)
        self.save()

    @Slot(str, result="QVariant")
    def getSubject(self, subject_id: str) -> Optional[Subject]:
        """获取科目信息"""
        return next((s for s in self.schedule.subjects if s.id == subject_id), None)

    # Day 操作
    @Slot(int, "QVariant", str, result=str)
    def addDay(self, day_of_week: int = 0, weeks = None, date: str = "") -> str:
        """添加日程"""
        day = DayEntry(
            id=generate_id("day"),
            entries=[],
            dayOfWeek=day_of_week or None,
            weeks=weeks,
            date=date or None
        )
        self.schedule.days.append(day)
        return day.id

    @Slot(str, int, "QVariant", str)
    def updateDay(self, day_id: str, day_of_week: int = 0,
                   weeks: Union[WeekType, str, List[int], int, None] = None, date: str = "") -> None:
        """更新日程"""
        day = self.getDay(day_id)
        if not day:
            return

        if day_of_week:
            day.dayOfWeek = day_of_week
        if weeks is not None:
            day.weeks = weeks
        if date:
            day.date = date

    @Slot(str)
    def removeDay(self, day_id: str) -> None:
        """删除日程"""
        day = self.getDay(day_id)
        if not day:
            return

        self.schedule.days.remove(day)

    @Slot(str, result="QVariant")
    def getDay(self, day_id: str) -> Optional[DayEntry]:
        """获取日程信息"""
        return next((d for d in self.schedule.days if d.id == day_id), None)

    # Entry 操作
    @Slot(str, str, str, str, str, str, result=str)
    def addEntry(self, day_id: str, entry_type: str,
                  start_time: str, end_time: str,
                  subject_id: str = "", title: str = "") -> str:
        """添加条目"""
        day = self.getDay(day_id)
        if not day:
            return ""

        entry = Entry(
            id=generate_id("entry"),
            type=EntryType(entry_type),
            startTime=start_time,
            endTime=end_time,
            subjectId=subject_id or None,
            title=title or None
        )
        day.entries.append(entry)
        return entry.id

    @Slot(str, str, str, str, str, str)
    def updateEntry(self, entry_id: str,
                     entry_type: str = "", start_time: str = "",
                     end_time: str = "", subject_id: str = "",
                     title: str = "") -> None:
        """更新条目"""
        entry = self.getEntry(entry_id)
        if not entry:
            logger.warning(f"Entry: {entry_id} not found")
            return

        if entry_type:
            entry.type = EntryType(entry_type)
        if start_time:
            entry.startTime = start_time
        if end_time:
            entry.endTime = end_time
        if subject_id:
            entry.subjectId = subject_id
        entry.title = title

    @Slot(str)
    def removeEntry(self, entry_id: str) -> None:
        """删除条目"""
        for day in self.schedule.days:
            entry = next((e for e in day.entries if e.id == entry_id), None)
            if entry:
                day.entries.remove(entry)
                return

    @Slot(str, result="QVariant")
    def getEntry(self, entry_id: str) -> Optional[Entry]:
        """获取条目信息"""
        for day in self.schedule.days:
            entry = next((e for e in day.entries if e.id == entry_id), None)
            if entry:
                return entry
        return None

    # 数据访问
    @Property("QVariant", notify=updated)
    def meta(self) -> Dict:
        """获取课程表元数据"""
        if not self.schedule or not self.schedule.meta:
            return {}
        return asdict(self.schedule.meta)

    @Property("QVariant", notify=updated)
    def subjects(self) -> List[Dict]:
        """获取所有科目"""
        if not self.schedule:
            return []
        return [asdict(subject) for subject in self.schedule.subjects]

    @Property("QVariant", notify=updated)
    def days(self) -> List[Dict]:
        """获取所有日程"""
        if not self.schedule:
            return []

        # 按时间排序
        sorted_days = []
        for day in self.schedule.days:
            day_dict = asdict(day)
            if 'entries' in day_dict and day_dict['entries']:
                day_dict['entries'].sort(key=lambda x: x.get('startTime', ''))
            sorted_days.append(day_dict)
        
        return sorted_days

    @Property("QVariant", notify=updated)
    def scheduleData(self) -> Dict:
        """获取完整的课程表数据"""
        if not self.schedule:
            return {}
        return asdict(self.schedule)