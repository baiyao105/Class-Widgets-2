from collections import defaultdict

from pydantic import BaseModel, ConfigDict, Field
from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QApplication

from src import __CSES_SCHEMA_VERSION__
from src.core.schedule.model import (
    Entry,
    EntryType,
    ScheduleData,
    Subject,
    Timeline,
    WeekType,
)
from src.core.utils import generate_id

from .common import build_meta, fill_short_breaks, to_cw_time


class CSESClass(BaseModel):
    subject: str | None = None
    start_time: str
    end_time: str

    model_config = ConfigDict(extra="allow")


class CSESSchedule(BaseModel):
    name: str = ""
    enable_day: int | None = None
    weeks: str = "all"
    classes: list[CSESClass] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class CSESSubject(BaseModel):
    name: str = "Unknown"
    simplified_name: str | None = None
    teacher: str | None = None
    room: str | None = None

    model_config = ConfigDict(extra="allow")


class CSESDocument(BaseModel):
    version: int
    subjects: list[CSESSubject] = Field(default_factory=list)
    schedules: list[CSESSchedule] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


def to_schedule(document: CSESDocument) -> ScheduleData:
    if document.version != __CSES_SCHEMA_VERSION__:
        raise ValueError(f"CSES schema version not supported: {document.version}")

    subjects: list[Subject] = []
    subject_id_map: dict[str, str] = {}
    for item in document.subjects:
        subject_id = generate_id("subj")
        subject_id_map[item.name] = subject_id
        subjects.append(
            Subject(
                id=subject_id,
                icon="ic_fluent_book_20_regular",
                name=item.name,
                simplifiedName=item.simplified_name,
                teacher=item.teacher,
                location=item.room,
            )
        )

    days: list[Timeline] = []
    for schedule in document.schedules:
        entries: list[Entry] = []
        for item in schedule.classes:
            subject_name = (item.subject or "").strip()
            subject_id = subject_id_map.get(subject_name)

            entries.append(
                Entry(
                    id=generate_id("entry"),
                    type=EntryType.CLASS,
                    subjectId=subject_id,
                    title=None if subject_id else subject_name or None,
                    startTime=to_cw_time(item.start_time),
                    endTime=to_cw_time(item.end_time),
                )
            )

        entries = fill_short_breaks(entries)

        match schedule.weeks:
            case "odd":
                weeks = WeekType.ODD
            case "even":
                weeks = WeekType.EVEN
            case _:
                weeks = WeekType.ALL

        days.append(
            Timeline(
                id=generate_id("day"),
                entries=entries,
                dayOfWeek=[schedule.enable_day] if schedule.enable_day else None,
                weeks=weeks,
            )
        )

    return ScheduleData(
        meta=build_meta(),
        subjects=subjects,
        days=days,
        overrides=[],
    )


def _convert_weeks_to_cses(weeks, max_week_cycle: int | None = None) -> str:
    if isinstance(weeks, WeekType):
        return weeks.value
    if isinstance(weeks, int) and max_week_cycle == 2:
        if weeks == 1:
            return "odd"
        if weeks == 2:
            return "even"
    return "all"


def _to_cses_time(time_str: str) -> str:
    if not time_str:
        raise ValueError(f"Get error type of time: {type(time_str)}; value: {time_str}")
    return f"{time_str}:00"


def _get_localized_day_name(dow: int) -> str:
    locale = QLocale()
    return locale.dayName(dow, QLocale.FormatType.LongFormat)


def _get_localized_week_label(week_str: str) -> str:
    if week_str == "all":
        return QApplication.translate("Schedule", "All Weeks")
    if week_str == "odd":
        return QApplication.translate("Schedule", "Odd Weeks")
    if week_str == "even":
        return QApplication.translate("Schedule", "Even Weeks")
    return week_str


def _ov_weeks_to_keys(ov_weeks, max_week_cycle: int) -> list[str]:
    if ov_weeks is None:
        return ["all"]
    if isinstance(ov_weeks, WeekType):
        return [ov_weeks.value]
    if isinstance(ov_weeks, int) and max_week_cycle == 2:
        return ["odd"] if ov_weeks == 1 else ["even"]
    return ["all"]


def from_schedule(schedule: ScheduleData) -> CSESDocument:
    subjects_map = {subject.id: subject for subject in schedule.subjects}
    override_map = defaultdict(list)

    for override in schedule.overrides:
        dows = override.dayOfWeek or [0]
        keys = _ov_weeks_to_keys(override.weeks, schedule.meta.maxWeekCycle)
        for dow in dows:
            for key in keys:
                override_map[(dow, key)].append(override)

    output_schedules: list[CSESSchedule] = []
    for day in schedule.days:
        day_dows = day.dayOfWeek or [0]
        day_weeks_str = _convert_weeks_to_cses(
            day.weeks, schedule.meta.maxWeekCycle
        )

        for dow in day_dows:
            base_classes = []
            for entry in day.entries:
                if entry.type != EntryType.CLASS:
                    continue
                subject_name = (
                    subjects_map.get(entry.subjectId).name
                    if entry.subjectId and entry.subjectId in subjects_map
                    else entry.title or ""
                )
                base_classes.append(
                    {
                        "subject": subject_name,
                        "start_time": _to_cses_time(entry.startTime),
                        "end_time": _to_cses_time(entry.endTime),
                        "entry_id": entry.id,
                    }
                )

            has_per_week_override = bool(
                ((dow, "odd") in override_map) or ((dow, "even") in override_map)
            )
            if day_weeks_str in ("odd", "even"):
                week_candidates = [day_weeks_str]
            elif day_weeks_str == "all" and has_per_week_override:
                week_candidates = ["odd", "even"]
            else:
                week_candidates = ["all"]

            for week_str in week_candidates:
                final_classes = [item.copy() for item in base_classes]

                for item in final_classes:
                    best_override = None
                    best_priority = -1

                    for week_key in (week_str, "all"):
                        for override in override_map.get((dow, week_key), []):
                            if not (
                                item["entry_id"] == override.entryId
                                and override.subjectId
                                and override.subjectId in subjects_map
                            ):
                                continue
                            priority = 1 if week_key == week_str else 0
                            if priority > best_priority:
                                best_override = override
                                best_priority = priority

                    if best_override:
                        item["subject"] = subjects_map[best_override.subjectId].name

                classes = [
                    CSESClass(
                        subject=item["subject"],
                        start_time=item["start_time"],
                        end_time=item["end_time"],
                    )
                    for item in final_classes
                ]
                name_label = _get_localized_week_label(week_str)
                output_schedules.append(
                    CSESSchedule(
                        name=f"{_get_localized_day_name(dow)} - {name_label}",
                        enable_day=dow,
                        weeks=week_str,
                        classes=classes,
                    )
                )

    output_subjects = [
        CSESSubject(
            name=subject.name,
            simplified_name=subject.simplifiedName,
            teacher=subject.teacher,
            room=subject.location,
        )
        for subject in schedule.subjects
    ]

    return CSESDocument(
        version=__CSES_SCHEMA_VERSION__,
        subjects=output_subjects,
        schedules=output_schedules,
    )


MODEL = CSESDocument
SERIALIZER = "yaml"
TO_SCHEDULE = to_schedule
FROM_SCHEDULE = from_schedule
