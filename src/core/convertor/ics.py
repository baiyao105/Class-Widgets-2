from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from math import lcm
from pathlib import Path
from typing import Any

import icalendar
import recurring_ical_events
from loguru import logger

from src.core.schedule.model import (
    Entry,
    EntryType,
    ScheduleData,
    Subject,
    Timeline,
)
from src.core.utils import generate_id

from .common import build_meta, fill_short_breaks

_BYDAY = {
    "MO": 1,
    "TU": 2,
    "WE": 3,
    "TH": 4,
    "FR": 5,
    "SA": 6,
    "SU": 7,
}


@dataclass(frozen=True)
class Occurrence:
    date: date
    start: datetime
    end: datetime
    summary: str
    location: str


@dataclass(frozen=True)
class InfiniteSpec:
    uid: str
    summary: str
    location: str
    start: datetime
    end: datetime
    interval: int
    weekdays: tuple[int, ...]
    first_date: date
    exdates: frozenset[date]
    rdates: tuple[date | datetime, ...]

    def positions(self, start_date: date, max_week_cycle: int) -> tuple[int, ...]:
        first_week = _week_index(self.first_date, start_date)
        phase = ((first_week - 1) % max_week_cycle) + 1
        result: list[int] = []
        position = phase
        while position not in result:
            result.append(position)
            position = ((position - 1 + self.interval) % max_week_cycle) + 1
        return tuple(sorted(result))

    def matches_pattern(self, value: date, start_date: date, max_week_cycle: int) -> bool:
        if value.isoweekday() not in self.weekdays:
            return False
        cycle_week = ((_week_index(value, start_date) - 1) % max_week_cycle) + 1
        return cycle_week in self.positions(start_date, max_week_cycle)

    def matches_date(self, value: date, start_date: date, max_week_cycle: int) -> bool:
        return (
            value >= self.first_date
            and value not in self.exdates
            and self.matches_pattern(value, start_date, max_week_cycle)
        )


def _first(value: Any) -> Any:
    if isinstance(value, (list, tuple)) and value:
        return value[0]
    return value


def _as_date(value: date | datetime) -> date:
    return value.date() if isinstance(value, datetime) else value


def _week_index(value: date, start_date: date) -> int:
    return (value - start_date).days // 7 + 1


def _local_datetime(value: datetime) -> datetime:
    return value.astimezone() if value.tzinfo is not None else value


def _component_time(component: Any, name: str) -> datetime | None:
    prop = component.get(name)
    if prop is None or not hasattr(prop, "dt"):
        return None
    value = prop.dt
    return value if isinstance(value, datetime) else None


def _component_times(component: Any) -> tuple[datetime, datetime] | None:
    start = _component_time(component, "DTSTART")
    if start is None:
        return None

    end = _component_time(component, "DTEND")
    if end is None:
        duration_prop = component.get("DURATION")
        duration = getattr(duration_prop, "dt", None)
        if not isinstance(duration, timedelta):
            return None
        end = start + duration

    start = _local_datetime(start)
    end = _local_datetime(end)
    if end <= start or start.date() != end.date():
        return None
    return start, end


def _component_text(component: Any, name: str) -> str:
    value = component.get(name)
    return str(value).strip() if value is not None else ""


def _rrule(component: Any) -> tuple[Any, str, int] | None:
    rule = component.get("RRULE")
    if rule is None:
        return None
    frequency = str(_first(rule.get("FREQ")) or "").upper()
    if not frequency:
        return None
    interval = int(_first(rule.get("INTERVAL")) or 1)
    return rule, frequency, interval


def _has_end_limit(rule: Any) -> bool:
    return bool(rule.get("UNTIL") or rule.get("COUNT"))


def _is_infinite_weekly(component: Any) -> bool:
    data = _rrule(component)
    return bool(data and data[1] == "WEEKLY" and not _has_end_limit(data[0]))


def _is_supported_component(component: Any) -> bool:
    if str(component.get("STATUS") or "").upper() == "CANCELLED":
        return False
    data = _rrule(component)
    return data is None or data[1] == "WEEKLY"


def _byday_weekdays(component: Any, start: datetime) -> tuple[int, ...]:
    data = _rrule(component)
    if data is None:
        return (start.isoweekday(),)
    byday = data[0].get("BYDAY")
    if not byday:
        return (start.isoweekday(),)
    values = byday if isinstance(byday, list) else [byday]
    result = []
    for value in values:
        text = str(value).upper()
        for token, weekday in _BYDAY.items():
            if token in text and weekday not in result:
                result.append(weekday)
    return tuple(sorted(result)) or (start.isoweekday(),)


def _iter_property_dates(value: Any):
    if value is None:
        return
    values = value if isinstance(value, list) else [value]
    for item in values:
        dates = getattr(item, "dts", None)
        if dates:
            for nested in dates:
                yield getattr(nested, "dt", nested)
        else:
            yield getattr(item, "dt", item)


def _property_dates(component: Any, name: str) -> tuple[date | datetime, ...]:
    return tuple(
        value
        for value in _iter_property_dates(component.get(name))
        if isinstance(value, (date, datetime))
    )


def _build_infinite_spec(component: Any, times: tuple[datetime, datetime]) -> InfiniteSpec | None:
    data = _rrule(component)
    if data is None:
        return None
    start, end = times
    exdates = frozenset(
        _as_date(value) for value in _property_dates(component, "EXDATE")
    )
    return InfiniteSpec(
        uid=str(component.get("UID") or ""),
        summary=_component_text(component, "SUMMARY"),
        location=_component_text(component, "LOCATION"),
        start=start,
        end=end,
        interval=data[2],
        weekdays=_byday_weekdays(component, start),
        first_date=start.date(),
        exdates=exdates,
        rdates=_property_dates(component, "RDATE"),
    )


def _occurrence(component: Any) -> Occurrence | None:
    if str(component.get("STATUS") or "").upper() == "CANCELLED":
        return None
    times = _component_times(component)
    if times is None:
        return None
    start, end = times
    return Occurrence(
        date=start.date(),
        start=start,
        end=end,
        summary=_component_text(component, "SUMMARY"),
        location=_component_text(component, "LOCATION"),
    )


def _finite_expansion_end(components: list[Any], start_date: date) -> date:
    value = start_date

    for component in components:
        times = _component_times(component)
        if times is None:
            continue
        start, end = times
        data = _rrule(component)
        candidate = end.date()
        if data is not None:
            rule, _frequency, interval = data
            count = int(_first(rule.get("COUNT")) or 0)
            until = _first(rule.get("UNTIL"))
            if count:
                candidate = (start + timedelta(weeks=(count - 1) * interval)).date()
            elif isinstance(until, (date, datetime)):
                candidate = _as_date(until)
        value = max(value, candidate)

    return max(value, start_date + timedelta(weeks=1)) + timedelta(days=1)


def _finite_calendar(calendar: Any, finite_components: list[Any]) -> Any:
    result = icalendar.Calendar()
    for component in calendar.subcomponents:
        if component.name == "VTIMEZONE":
            result.add_component(component)
    for component in finite_components:
        result.add_component(component)
    return result


def _expand_finite(
    calendar: Any,
    finite_components: list[Any],
    start_date: date,
) -> list[Occurrence]:
    if not finite_components:
        return []
    result_calendar = _finite_calendar(calendar, finite_components)
    start = datetime.combine(start_date, time.min)
    end_date = _finite_expansion_end(finite_components, start_date)
    end = datetime.combine(end_date, time.max)
    components = recurring_ical_events.of(result_calendar).between(start, end)
    result = []
    for component in components:
        occurrence = _occurrence(component)
        if occurrence and occurrence.date >= start_date:
            result.append(occurrence)
    return result


def _unique_occurrences(occurrences: list[Occurrence]) -> list[Occurrence]:
    result = []
    seen = set()
    for occurrence in occurrences:
        key = (
            occurrence.date,
            occurrence.start,
            occurrence.end,
            occurrence.summary,
            occurrence.location,
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(occurrence)
    return result


def _rdate_occurrences(spec: InfiniteSpec) -> list[Occurrence]:
    result = []
    duration = spec.end - spec.start
    for value in spec.rdates:
        if isinstance(value, datetime):
            start = _local_datetime(value)
        else:
            start = datetime.combine(value, spec.start.timetz())
        result.append(
            Occurrence(
                date=start.date(),
                start=start,
                end=start + duration,
                summary=spec.summary,
                location=spec.location,
            )
        )
    return result


def _signature(entries: list[Entry]) -> tuple:
    return tuple(
        sorted(
            (
                entry.type.value,
                entry.subjectId,
                entry.title,
                entry.startTime,
                entry.endTime,
            )
            for entry in entries
        )
    )


def _subject_key(summary: str, location: str) -> tuple[str, str] | None:
    if not summary:
        return None
    return summary, location


def _entry_for(
    summary: str,
    location: str,
    start: datetime,
    end: datetime,
    subjects: dict[tuple[str, str], str],
) -> Entry:
    key = _subject_key(summary, location)
    subject_id = subjects.get(key) if key else None
    return Entry(
        id=generate_id("entry"),
        type=EntryType.CLASS,
        subjectId=subject_id,
        title=None if subject_id else summary or None,
        startTime=start.strftime("%H:%M"),
        endTime=end.strftime("%H:%M"),
    )


def _collect_infinite(
    components: list[Any],
) -> tuple[list[InfiniteSpec], set[str], dict[str, set[date]]]:
    specs = []
    uids: set[str] = set()
    suppressed: dict[str, set[date]] = defaultdict(set)

    for component in components:
        if not _is_supported_component(component) or not _is_infinite_weekly(component):
            continue
        times = _component_times(component)
        if times is None:
            continue
        spec = _build_infinite_spec(component, times)
        if spec is None:
            continue
        specs.append(spec)
        uids.add(spec.uid)

    for component in components:
        uid = str(component.get("UID") or "")
        if uid not in uids:
            continue
        recurrence_id = component.get("RECURRENCE-ID")
        if recurrence_id is not None and hasattr(recurrence_id, "dt"):
            suppressed[uid].add(_as_date(recurrence_id.dt))

    return specs, uids, suppressed


def _read(path: str | Path, start_date: date | str) -> ScheduleData:
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    calendar = icalendar.Calendar.from_ical(Path(path).read_bytes())
    components = list(calendar.walk("VEVENT"))
    infinite_specs, _infinite_uids, suppressed = _collect_infinite(components)

    finite_components = [
        component
        for component in components
        if _is_supported_component(component) and not _is_infinite_weekly(component)
    ]
    finite_occurrences = _expand_finite(calendar, finite_components, start_date)
    finite_occurrences.extend(
        occurrence
        for spec in infinite_specs
        for occurrence in _rdate_occurrences(spec)
        if occurrence.date >= start_date
    )
    finite_occurrences = _unique_occurrences(finite_occurrences)

    max_week_cycle = 1
    for spec in infinite_specs:
        max_week_cycle = lcm(max_week_cycle, spec.interval)

    subjects: dict[tuple[str, str], str] = {}
    subject_list: list[Subject] = []
    subject_values = [
        (spec.summary, spec.location)
        for spec in infinite_specs
    ] + [
        (occurrence.summary, occurrence.location)
        for occurrence in finite_occurrences
    ]
    for summary, location in subject_values:
        key = _subject_key(summary, location)
        if key is None or key in subjects:
            continue
        subject_id = generate_id("subj")
        subjects[key] = subject_id
        subject_list.append(
            Subject(
                id=subject_id,
                name=summary,
                location=location or None,
                isLocalClassroom=not bool(location),
            )
        )

    base_groups: dict[tuple[int, int], list[Entry]] = defaultdict(list)
    for spec in infinite_specs:
        for weekday in spec.weekdays:
            for position in spec.positions(start_date, max_week_cycle):
                base_groups[(weekday, position)].append(
                    _entry_for(
                        spec.summary,
                        spec.location,
                        spec.start,
                        spec.end,
                        subjects,
                    )
                )

    finite_by_date: dict[date, list[Occurrence]] = defaultdict(list)
    for occurrence in finite_occurrences:
        finite_by_date[occurrence.date].append(occurrence)

    special_dates = set(finite_by_date)
    for spec in infinite_specs:
        special_dates.update(spec.exdates)
        special_dates.update(suppressed.get(spec.uid, set()))
        if spec.first_date > start_date:
            current = start_date
            while current < spec.first_date:
                if spec.matches_pattern(current, start_date, max_week_cycle):
                    special_dates.add(current)
                current += timedelta(days=1)

    special_groups: dict[tuple[int, tuple], set[int]] = defaultdict(set)
    special_entries: dict[tuple[int, tuple], list[Entry]] = {}
    for day in sorted(special_dates):
        entries = []
        for spec in infinite_specs:
            if spec.matches_date(day, start_date, max_week_cycle):
                if day in suppressed.get(spec.uid, set()):
                    continue
                entries.append(
                    _entry_for(
                        spec.summary,
                        spec.location,
                        spec.start,
                        spec.end,
                        subjects,
                    )
                )
        entries.extend(
            _entry_for(
                occurrence.summary,
                occurrence.location,
                occurrence.start,
                occurrence.end,
                subjects,
            )
            for occurrence in finite_by_date.get(day, [])
        )
        entries = fill_short_breaks(entries)
        signature = _signature(entries)
        key = (day.isoweekday(), signature)
        special_groups[key].add(_week_index(day, start_date))
        special_entries.setdefault(key, entries)

    timelines: list[Timeline] = []
    for (weekday, _signature_value), weeks in sorted(
        special_groups.items(),
        key=lambda item: (item[0][0], item[0][1]),
    ):
        timelines.append(
            Timeline(
                id=generate_id("day"),
                dayOfWeek=[weekday],
                weeks=sorted(weeks),
                entries=special_entries[(weekday, _signature_value)],
            )
        )

    for (weekday, position), entries in sorted(base_groups.items()):
        timelines.append(
            Timeline(
                id=generate_id("day"),
                dayOfWeek=[weekday],
                weeks=position,
                entries=fill_short_breaks(entries),
            )
        )

    if not timelines:
        logger.warning(f"No supported ICS events found in {path}")

    return ScheduleData(
        meta=build_meta(start_date=start_date, max_week_cycle=max_week_cycle),
        subjects=subject_list,
        days=timelines,
        overrides=[],
    )


def read(path: str | Path, start_date: date | str) -> ScheduleData:
    return _read(path, start_date)


def validate(path: str | Path) -> bool:
    try:
        calendar = icalendar.Calendar.from_ical(Path(path).read_bytes())
        return any(component.name == "VEVENT" for component in calendar.walk())
    except Exception:
        return False


READ = read
