from enum import Enum

from pydantic import BaseModel, Field, Extra, validator
from typing import Dict, List, Optional, Any

from ..directories import DEFAULT_THEME


class LayoutAnchor(str, Enum):
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


class AppConfig(BaseModel):
    dev_mode: bool = False
    no_logs: bool = False
    version: str = "0.0.1"
    channel: str = "alpha"

class ScheduleConfig(BaseModel):
    current_schedule: str = "default"
    preparation_time: int = 2

class WidgetEntry(BaseModel):
    type_id: str
    instance_id: str
    settings: Optional[Dict[str, Any]] = {}


class PreferencesConfig(BaseModel):
    current_theme: str = Field(default_factory=lambda: DEFAULT_THEME.as_uri())
    scale_factor: float = 1.0  # 缩放比例
    opacity: float = 1.0  # 不透明度
    widgets_anchor: LayoutAnchor = LayoutAnchor.TOP_CENTER  # 全局对齐方式
    widgets_offset_x: int = 0  # 全局水平偏移
    widgets_offset_y: int = 24  # 全局垂直偏移

    widgets_presets: Dict[str, List[WidgetEntry]] = Field(
        default_factory=lambda: {
            "default": [
                WidgetEntry(type_id="classwidgets.time", instance_id="8ee721ef-ab36-4c23-834d-2c666a6739a3"),
                WidgetEntry(type_id="classwidgets.hello", instance_id="87985398-2844-4c9e-b27d-6ea81cd0a2c6"),
            ]
        }
    )
    current_preset: str = "default"

    class Config:
        use_enum_values = True
        extra = Extra.allow

class PluginsConfig(BaseModel):
    enabled: List[str] = ["builtin.classwidgets.widgets"]