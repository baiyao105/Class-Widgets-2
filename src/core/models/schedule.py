from pydantic import BaseModel
from typing import Optional, List, Dict, Union
from enum import Enum


class EntryType(str, Enum):
    CLASS = "class"
    BREAK = "break"
    ACTIVITY = "activity"
    FREE = "free"
    PREPARATION = "preparation"


class WeekType(str, Enum):
    ALL = "all"


class Subject(BaseModel):
    id: str
    name: str
    simplifiedName: Optional[str] = None
    teacher: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    location: Optional[str] = None
    isLocalClassroom: bool = True


class Entry(BaseModel):
    id: str
    type: EntryType
    startTime: str
    endTime: str
    subjectId: Optional[str] = None
    title: Optional[str] = None


class DayEntry(BaseModel):
    id: str
    entries: List[Entry]
    dayOfWeek: Union[List[int], int, None] = None  # 1~7
    weeks: Union[WeekType, List[int], int, None] = None  # all, 多选周期数，单选周期数
    date: Optional[str] = None


class MetaInfo(BaseModel):
    id: str
    version: int
    maxWeekCycle: int
    startDate: str


class EntryOverride(BaseModel):
    dayOfWeek: Union[List[int], int, None] = None  # 1~7
    weeks: Union[WeekType, List[int], int, None] = None  # all, 多选周期数，单选周期数
    subjectId: Optional[str] = None
    title: Optional[str] = None


class ScheduleData(BaseModel):
    meta: MetaInfo
    subjects: List[Subject]
    days: List[DayEntry]
    entries: Dict[str, EntryOverride] = {}
