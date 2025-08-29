from pydantic import BaseModel
from typing import Optional, List, Union
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
    dayOfWeek: Optional[int] = 1  # 1~7
    weeks: Union[WeekType, List[int], int, None] = None
    date: Optional[str] = None


class MetaInfo(BaseModel):
    id: str
    version: int
    maxWeekCycle: int
    startDate: str


class ScheduleData(BaseModel):
    meta: MetaInfo
    subjects: List[Subject]
    days: List[DayEntry]
