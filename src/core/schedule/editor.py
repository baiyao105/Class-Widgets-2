from datetime import datetime
from typing import Optional, List, Dict, Union

from PySide6.QtCore import QObject, Property, Signal, Slot
from loguru import logger

from src.core.schedule import ScheduleData, Subject, Timeline, Entry, EntryType
from src.core.schedule.model import WeekType, Timetable
from src.core.schedule import ScheduleManager
from src.core.utils import generate_id, get_default_subjects


class ScheduleEditor(QObject):
    updated = Signal()

    def __init__(self, manager: ScheduleManager):
        super().__init__()
        self.manager = manager
        self._filename = manager.schedule_path.stem
        self.schedule: ScheduleData = self.manager.schedule
        self.updated.connect(self.refresh_manager)
        self.manager.scheduleSwitched.connect(self.refresh)

    def refresh(self, schedule: ScheduleData):  # 接受来自 manager 的更新
        self.schedule = schedule
        self._filename = self.manager.schedule_path.stem

    def refresh_manager(self):
        self.manager.modify(self.schedule)  # 提交给 manager

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
        self.updated.emit()
        return subject.id

    @Slot(str, str, str, str, str, str, str, bool)
    def updateSubject(self, subject_id: str, name: str = "", simplified_name = "", teacher: str = "",
                      icon: str = "", color: str = "", location: str = "", is_local_classroom: bool = True) -> None:
        """更新科目"""
        subject = self.getSubject(subject_id)
        if not subject:
            return

        if name:
            subject.name = name
        if simplified_name:
            subject.simplifiedName = simplified_name
        if teacher:
            subject.teacher = teacher
        if icon:
            subject.icon = icon
        if color:
            subject.color = color
        if location:
            subject.location = location
        subject.isLocalClassroom = is_local_classroom
        self.updated.emit()

    @Slot(str)
    def removeSubject(self, subject_id: str) -> None:
        """删除科目"""
        subject = self.getSubject(subject_id)
        if not subject:
            return

        # 删除相关的课程条目
        for day in self.schedule.days:
            day.entries = [e for e in day.entries if e.subjectId != subject_id]

        self.schedule.subjects.remove(subject)
        self.updated.emit()

    @Slot(str, result="QVariant")
    def getSubject(self, subject_id: str) -> Optional[Subject]:
        """获取科目信息"""
        return next((s for s in self.schedule.subjects if s.id == subject_id), None)

    # Day 操作
    @Slot(list, "QVariant", str, result=str)
    def addDay(self, day_of_week: list = None, weeks = None, date: str = "") -> str:
        """添加日程"""
        day = Timeline(
            id=generate_id("day"),
            entries=[],
            dayOfWeek=day_of_week or None,
            weeks=weeks,
            date=date or None
        )
        self.schedule.days.append(day)
        self.updated.emit()
        return day.id

    @Slot(str, list, "QVariant", str)
    def updateDay(self, day_id: str, day_of_week: list = None,
                   weeks: Union[WeekType, str, List[int], str, int, None] = None, date: str = "") -> None:
        """更新日程"""
        day = self.getDay(day_id)
        if not day:
            return

        if day_of_week:
            day.dayOfWeek = day_of_week
        if weeks is not None:
            if isinstance(weeks, int):
                day.weeks = weeks
            elif isinstance(weeks, str) and weeks == WeekType.ALL.value:
                day.weeks = WeekType.ALL
            elif isinstance(weeks, list):
                day.weeks = weeks
            else:
                day.weeks = None
        if date:
            day.date = date
        self.updated.emit()

    @Slot(str)
    def removeDay(self, day_id: str) -> None:
        """删除日程"""
        day = self.getDay(day_id)
        if not day:
            logger.warning(f"Day: {day_id} not found")
            return

        self.schedule.days.remove(day)
        self.updated.emit()

    @Slot(str, result="QVariant")
    def getDay(self, day_id: str) -> Optional[Timeline]:
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
        day.entries.sort(key=lambda e: e.startTime)  # 排序
        self.updated.emit()
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
        entry.subjectId = subject_id
        entry.title = title

        for day in self.schedule.days:  # 排序
            if entry in day.entries:
                day.entries.sort(key=lambda e: e.startTime)
                break
        self.updated.emit()

    @Slot(str)
    def removeEntry(self, entry_id: str) -> None:
        """删除条目"""
        for day in self.schedule.days:
            entry = next((e for e in day.entries if e.id == entry_id), None)
            if entry:
                day.entries.remove(entry)
                self.updated.emit()
                return

    @Slot(str, result="QVariant")
    def getEntry(self, entry_id: str) -> Optional[Entry]:
        """获取条目信息"""
        for day in self.schedule.days:
            entry = next((e for e in day.entries if e.id == entry_id), None)
            if entry:
                return entry
        return None

    # Override
    @Slot(str, list, "QVariant", result=str)
    def findOverride(self, entry_id: str, day_of_week, weeks) -> Optional[str]:
        """
        查找已有 override，返回其 id，如不存在返回空字符串
        """
        day_of_week_list = day_of_week or None
        for o in self.schedule.overrides:
            if o.entryId != entry_id:
                continue
            if o.dayOfWeek != day_of_week_list:
                continue
            if o.weeks != weeks:
                continue
            return o.id
        return None

    @Slot(str, list, "QVariant", str, str, result=bool)
    def addOverride(self, entry_id: str, day_of_week, weeks, subject_id="", title=""):

        override = Timetable(
            id=generate_id("override"),
            entryId=entry_id,
            dayOfWeek=day_of_week,
            weeks=weeks,
            subjectId=subject_id or None,
            title=title or None
        )
        self.schedule.overrides.append(override)
        self.updated.emit()
        return True

    @Slot(str, str, str, result=bool)
    def updateOverride(self, override_id: str, subject_id=None, title=None):
        for o in self.schedule.overrides:
            if o.id == override_id:
                if subject_id is not None:
                    o.subjectId = subject_id
                if title is not None:
                    o.title = title
                self.updated.emit()
                return True
        return False

    @Slot(str, result=bool)
    def removeOverride(self, override_id: str):
        for override in self.schedule.overrides:
            if override.id == override_id:
                self.schedule.overrides.remove(override)
                self.updated.emit()
                return True
        return False

    @Slot(str, result=str)
    def subjectNameById(self, subject_id: str) -> Optional[str]:
        """根据 ID 获取科目名称"""
        subject = self.getSubject(subject_id)
        if subject:
            return subject.name
        return None

    @Slot(str, int, int, result="QVariant")
    def getEntryOverride(self, entry_id: str, week: int, weekday: int):
        """
        返回套用 overrides 的 entry 对象
        """
        entry = self.getEntry(entry_id)
        if not entry:
            return None

        # 先转 dict
        data = entry.model_dump()
        applicable = None

        for o in self.schedule.overrides:
            if o.entryId != entry_id:
                continue

            valid_day = not o.dayOfWeek or weekday in o.dayOfWeek
            valid_week = (
                    week == -1
                    or not o.weeks
                    or o.weeks == "all"
                    or (isinstance(o.weeks, list) and week in o.weeks)
                    or (isinstance(o.weeks, int) and o.weeks == week)
            )

            if valid_day and valid_week:
                if o.weeks != "all":
                    applicable = o
                    break  # 优先具体周
                elif applicable is None:
                    applicable = o  # 没有具体周才用 all

        if applicable:
            if applicable.subjectId:
                data["subjectId"] = applicable.subjectId
            if applicable.title:
                data["title"] = applicable.title

        return data

    # 加急做的，要发prerelease了忘记做了也是神人了
    @Slot(str, result=bool)
    def setStartDate(self, date_str: str) -> bool:
        """
        设置开学日期，格式: yyyy-mm-dd
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            logger.warning(f"Invalid date format: {date_str}")
            return False

        if not self.schedule or not self.schedule.meta:
            logger.warning("No schedule or meta data available.")
            return False

        self.schedule.meta.startDate = date_str
        self.updated.emit()
        return True

    @Slot(result=str)
    def getStartDate(self) -> str:
        """
        获取当前开学日期
        """
        if not self.schedule or not self.schedule.meta:
            return datetime.now().strftime("%Y-%m-%d")
        return getattr(self.schedule.meta, "startDate", datetime.now().strftime("%Y-%m-%d"))

    @Slot(result=bool)
    def restoreDefaultSubjects(self):
        """加载默认学科"""
        default_subjects = get_default_subjects()
        self.schedule.subjects.clear()
        for subj in default_subjects:
            self.schedule.subjects.append(subj)
        self.updated.emit()

    # 数据访问
    @Property("QVariant", notify=updated)
    def meta(self) -> Dict:
        """获取课程表元数据"""
        if not self.schedule or not self.schedule.meta:
            return {}
        return self.schedule.meta.model_dump()

    @Property(list, notify=updated)
    def subjects(self) -> List[Dict]:
        """获取所有科目"""
        if not self.schedule:
            return []
        return [subject.model_dump() for subject in self.schedule.subjects]

    @Property(list, notify=updated)
    def days(self) -> List[Dict]:
        """获取所有日程"""
        if not self.schedule:
            return []

        return [day.model_dump() for day in self.schedule.days]

    @Property(list, notify=updated)
    def overrides(self) -> List[Timetable]:
        """获取所有条目"""
        if not self.schedule:
            return []

        return [override.model_dump() for override in self.schedule.overrides]

    @Property("QVariant", notify=updated)
    def scheduleData(self) -> Dict:
        """获取完整的课程表数据"""
        if not self.schedule:
            return {}
        return self.schedule.model_dump()

    @Property("QVariant", notify=updated)
    def path(self) -> str:
        """获取课程表文件路径"""
        return self.manager.schedule_path.as_uri()

    @Property("QVariant", notify=updated)
    def filename(self) -> str:
        """获取课程表文件名"""
        return self._filename