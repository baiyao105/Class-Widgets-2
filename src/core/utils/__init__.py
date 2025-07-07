from PySide6.QtWidgets import QApplication

from .json_loader import JsonLoader
from .calculator import get_cycle_week, get_week_number
from uuid import uuid4


# Parser
def generate_id(prefix: str = "id") -> str:
    return f"{prefix}_{uuid4().hex}"

def to_dict(obj):
    from enum import Enum
    if isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, "__dataclass_fields__"):
        return {k: to_dict(getattr(obj, k)) for k in obj.__dataclass_fields__}
    elif isinstance(obj, (list, tuple)):
        return [to_dict(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    else:
        return obj

def qsTr(text: str):
    print(__name__)
    return QApplication.translate(__name__,text)
