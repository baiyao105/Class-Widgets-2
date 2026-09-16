from pathlib import Path

from pydantic import BaseModel

from src.core.schedule.model import ScheduleData

from . import cw1, cw2, cses
from .common import DUMPERS, LOADERS, auto_map

FORMATS = {
    "cw1": cw1,
    "cw2": cw2,
    "cses": cses,
}


def _get_format(format_id: str):
    normalized = format_id.strip().lower()
    try:
        return FORMATS[normalized]
    except KeyError as e:
        raise ValueError(f"Unsupported schedule format: {format_id}") from e


def read(source: str | Path, source_format: str) -> ScheduleData:
    module = _get_format(source_format)
    raw = LOADERS[module.SERIALIZER](source)
    document = module.MODEL.model_validate(raw)

    mapper = getattr(module, "TO_SCHEDULE", None)
    return mapper(document) if mapper else auto_map(document, ScheduleData)


def write(schedule: ScheduleData, target: str | Path, target_format: str) -> Path:
    module = _get_format(target_format)
    mapper = getattr(module, "FROM_SCHEDULE", None)

    if mapper:
        document = mapper(schedule)
    else:
        try:
            document = auto_map(schedule, module.MODEL)
        except Exception as e:
            raise ValueError(f"Format does not support writing: {target_format}") from e

    data = document.model_dump(mode="json") if isinstance(document, BaseModel) else document
    return DUMPERS[module.SERIALIZER](data, target)


def convert(
    source: str | Path,
    source_format: str,
    target: str | Path,
    target_format: str,
) -> Path:
    schedule = read(source, source_format)
    return write(schedule, target, target_format)
