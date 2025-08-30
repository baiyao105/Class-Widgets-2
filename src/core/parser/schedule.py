import json
from loguru import logger
from pathlib import Path
from typing import Union, Optional

from src.core.models.schedule import ScheduleData, MetaInfo, Subject, Entry, EntryType, DayEntry
from src.core.utils import generate_id
from src.core.utils.json_loader import JsonLoader

SCHEMA_VERSION = 1


class ScheduleParser:
    def __init__(self, path: Union[Path, str]):
        self.loader = JsonLoader(path)
        self.schedule: Optional[ScheduleData] = None
        self.schedule_dict: Optional[dict] = None

    @staticmethod
    def validate(data: dict) -> bool:
        return (
            isinstance(data, dict)
            and "meta" in data
            and isinstance(data["meta"], dict)
            and "version" in data["meta"]
            and "startDate" in data["meta"]
        )

    def load(self) -> ScheduleData:
        try:
            data = self.loader.load()
        except FileNotFoundError:
            raise FileNotFoundError("Schedule File not found")
        except json.decoder.JSONDecodeError as e:
            raise json.decoder.JSONDecodeError(f"JSON解析错误: {e}", e.doc, e.pos)
        except Exception as e:
            raise ValueError(f"Unexpected error: {e}")

        if not self.validate(data):
            raise ValueError("Invalid Schedule File")

        schedule = ScheduleData.model_validate(data)

        if schedule.meta.version != SCHEMA_VERSION:
            raise ValueError(f"Unsupported schema version: {schedule.meta.version}")

        self.schedule = schedule
        self.schedule_dict = schedule.model_dump()
        return self.schedule
