from pathlib import Path
from loguru import logger
from pydantic import BaseModel, Field, PrivateAttr
from PySide6.QtCore import QObject, QTimer, Signal, Property, Slot

from .model import AppConfig, ScheduleConfig, PreferencesConfig, PluginsConfig, LocaleConfig


class RootConfig(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    locale: LocaleConfig = Field(default_factory=LocaleConfig)
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
    configChanged = Signal()

    def __init__(self, path: Path, filename: str):
        super().__init__()
        self.path = Path(path)
        self.filename = filename
        self.full_path = self.path / filename

        self._config = RootConfig()
        self._config._on_change = lambda: self.save(silent=True)

        self.save_timer = QTimer(self)
        self.save_timer.setInterval(1000 * 60)  # 1分钟保存一次
        self.save_timer.timeout.connect(self.save)

    def load_config(self):
        if self.full_path.exists():
            try:
                data = self.full_path.read_text(encoding="utf-8")
                self._config = RootConfig.model_validate_json(data)
                self._config._on_change = lambda: self.save(silent=True)
            except Exception as e:
                logger.warning(f"配置文件读取失败: {e}, 使用默认配置")
        self.save()

    def save(self, silent=False):
        try:
            self.path.mkdir(parents=True, exist_ok=True)
            self.full_path.write_text(self._config.model_dump_json(indent=4), encoding="utf-8")
            if not silent:
                logger.success(f"配置保存成功: {self.full_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")

    def __getattr__(self, name):
        """代理属性获取"""
        if name == '_config':
            return self.__dict__['_config']

        return getattr(self._config, name)

    @Property('QVariant', notify=configChanged)
    def data(self):
        return self._config.model_dump()  # 整个配置转 dict

    @Slot(str, 'QVariant')
    def set(self, key: str, value):
        keys = key.split('.')  # 支持点分层，如 "preferences.current_theme"
        cfg = self._config
        for k in keys[:-1]:
            cfg = getattr(cfg, k)
        setattr(cfg, keys[-1], value)
        self._config._on_change()
        self.configChanged.emit()