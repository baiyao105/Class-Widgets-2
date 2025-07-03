import json

from loguru import logger

from src.core.models import *
from src.core.utils import generate_id, to_dict
from src.core.utils.json_loader import JsonLoader
from pathlib import Path
from typing import Union, Optional


class ScheduleParser:
    def __init__(self, path: Union[Path, str]):
        self.loader = JsonLoader(path)
        self.schedule: Optional[ScheduleData] = None
        self.schedule_dict: Optional[dict] = None

    @staticmethod
    def validate(data: dict) -> bool:  # 验证
        return (
            isinstance(data, dict) and
            "meta" in data and
            isinstance(data["meta"], dict) and
            "version" in data["meta"] and
            "startDate" in data["meta"]
        )

    def load(self) -> ScheduleData:
        try:
            data = self.loader.load()
        except FileNotFoundError:
            raise FileNotFoundError("Schedule File not found")
        except json.decoder.JSONDecodeError:
            raise json.decoder.JSONDecodeError
        except Exception as e:
            raise ValueError(f"Unexpected error: {e}")

        if not self.validate(data):
            raise ValueError("Invalid Schedule File")

        meta_data = data["meta"]
        meta = MetaInfo(
            id=meta_data.get("id") or generate_id("meta"),
            version=meta_data["version"],
            max_week_cycle=meta_data["maxWeekCycle"],
            start_date=meta_data["startDate"]
        )

        if meta.version != SCHEMA_VERSION:
            raise ValueError(f"Unsupported schema version: {meta.version}")

        subjects = [
            Subject(
                id=subject.get("id") or generate_id("subj"),
                name=subject["name"],
                teacher=subject.get("teacher"),
                icon=subject.get("icon"),
                location=subject.get("location"),
                is_local_classroom=subject.get("isLocalClassRoom", True)
            )
            for subject in data.get("subjects", [])
        ]

        subject_ids = {subject.id for subject in subjects}

        days = []
        for day in data.get("days", []):
            entries = []
            for e in day.get("entries", []):
                e_type = EntryType(e["type"])
                entry = Entry(
                    id=e.get("id") or generate_id("entry"),
                    type=e_type,
                    start_time=e["startTime"],
                    end_time=e["endTime"],
                    subject_id=e.get("subjectId"),
                    title=e.get("title")
                )
                if e_type == EntryType.CLASS and entry.subject_id not in subject_ids:
                    raise ValueError(f"无效的 subjectId: {entry.subject_id}")
                entries.append(entry)

            day_entry = DayEntry(
                id=day.get("id") or generate_id("day"),
                entries=entries,
                day_of_week=day.get("dayOfWeek"),
                weeks=day.get("weeks"),
                date=day.get("date")
            )
            days.append(day_entry)

        self.schedule_dict = to_dict(self.schedule)
        self.schedule = ScheduleData(meta=meta, subjects=subjects, days=days)
        return self.schedule

    # def get_meta(self) -> Optional[MetaInfo]:
    #     return self.schedule.meta if self.schedule else None
    #
    # def get_day_by_id(self, day_id: str) -> Optional[DayEntry]:
    #     return next((d for d in self.schedule.days if d.id == day_id), None)
    #
    # def get_subject_by_id(self, subject_id: str) -> Optional[Subject]:
    #     return next((subject for subject in self.schedule.subjects if subject.id == subject_id), None)
    #
    # def get_entry_by_id(self, entry_id: str) -> Optional[Entry]:
    #     for day in self.schedule.days:
    #         for entry in day.entries:
    #             if entry.id == entry_id:
    #                 return entry
    #     return None


if __name__ == "__main__":
    from src.core import EXAMPLES_PATH

    parser = ScheduleParser(EXAMPLES_PATH / "schedule" / "example.json")
    parser.load()

    print(f"\n{"Schedule":=^20}")
    print(parser.schedule)

    print(f"\n{'Meta':=^20}")
    print(parser.schedule.meta)

    print(f"\n{'Subjects':=^20}")
    for s in parser.schedule.subjects:
        print(s)

    print(f"\n{'Days':=^20}")
    for day in parser.schedule.days:
        print(day)
        for entry in day.entries:
            print(entry)
        print()
