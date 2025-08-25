from PySide6.QtWidgets import QApplication

from .json_loader import JsonLoader
from .calculator import get_cycle_week, get_week_number
from .tray import TrayIcon
from uuid import uuid4


# Parser
def generate_id(prefix: str = "id") -> str:
    return f"{prefix}_{uuid4().hex}"

# def to_dict(obj):
#     from enum import Enum
#     if isinstance(obj, Enum):
#         return obj.value
#     elif hasattr(obj, "__dataclass_fields__"):
#         return {k: to_dict(getattr(obj, k)) for k in obj.__dataclass_fields__}
#     elif isinstance(obj, (list, tuple)):
#         return [to_dict(i) for i in obj]
#     elif isinstance(obj, dict):
#         return {k: to_dict(v) for k, v in obj.items()}
#     else:
#         return obj

# qml context
import re

def is_valid_context_property_name(name: str) -> bool:
    # 只能包含字母数字和下划线，不能以数字开头，不能为空
    if not name:
        return False
    return bool(re.match(r'^[a-zA-Z_]\w*$', name))
