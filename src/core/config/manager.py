from pathlib import Path
from loguru import logger
from pydantic import BaseModel, Field, PrivateAttr, Extra
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, QTimer
from src.core.directories import DEFAULT_THEME


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
        extra = Extra.allow

class PluginsConfig(BaseModel):
    enabled: List[str] = ["builtin.classwidgets.widgets"]

class RootConfig(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    preferences: PreferencesConfig = Field(default_factory=PreferencesConfig)
    plugins: PluginsConfig = Field(default_factory=PluginsConfig)

    _on_change: callable = PrivateAttr(default=None)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if self._on_change and name != "_on_change":
            self._on_change()


# 配置管理器
class ConfigManager(QObject):
    def __init__(self, path: Path, filename: str):
        super().__init__()
        self.path = Path(path)
        self.filename = filename
        self.full_path = self.path / filename

        self._config = RootConfig()
        self._config._on_change = self.save

        self.save_timer = QTimer(self)
        self.save_timer.setInterval(1000 * 60)  # 1分钟保存一次
        self.save_timer.timeout.connect(self.save)

    def load_config(self):
        if self.full_path.exists():
            try:
                data = self.full_path.read_text(encoding="utf-8")
                self._config = RootConfig.model_validate_json(data)
                self._config._on_change = self.save
            except Exception as e:
                logger.warning(f"配置文件读取失败: {e}, 使用默认配置")
        self.save()

    def save(self):
        try:
            self.path.mkdir(parents=True, exist_ok=True)
            self.full_path.write_text(self._config.model_dump_json(indent=4), encoding="utf-8")
            logger.success(f"配置保存成功: {self.full_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")

    def __getattr__(self, name):
        """代理属性获取"""
        if name == '_config':
            return self.__dict__['_config']

        return getattr(self._config, name)