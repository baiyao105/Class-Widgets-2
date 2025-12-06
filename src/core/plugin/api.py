from pathlib import Path
from typing import Optional, List, Dict, Union
from datetime import datetime
from PySide6.QtCore import Signal, QUrl
from loguru import logger

from src.core.schedule.model import EntryType
from PySide6.QtCore import QObject


class WidgetsAPI:
    def __init__(self, app):
        self._app = app

    def register(self, widget_id: str, name: str, qml_path: Union[str, QUrl],
                 backend_obj: QObject = None,
                 settings_qml: Optional[Union[str, QUrl]] = None,
                 default_settings: Optional[dict] = None):
        self._app.widgets_model.add_widget(
            widget_id, name, qml_path, backend_obj, settings_qml, default_settings
        )


class NotifyAPI(QObject):
    pushed = Signal(str)  # 给插件监听的信号暂定

    def __init__(self, app):
        super().__init__()
        self._app = app
        app.notification.notify.connect(self.pushed.emit)

    def send(self, message: str):
        self._app.notification.push_activity(message)


class ScheduleAPI:
    def __init__(self, app):
        self._app = app

    def get(self):
        return self._app.schedule

    def reload(self):
        self._app.reloadSchedule()


class ThemeAPI(QObject):
    changed = Signal(str)

    def __init__(self, app):
        super().__init__()
        self._app = app
        app.theme_manager.themeChanged.connect(self.changed.emit)

    def current(self) -> Optional[str]:
        return self._app.theme_manager.current_theme


class RuntimeAPI(QObject):
    """暴露 ScheduleRuntime 的状态给插件"""
    updated = Signal()       # 课表/时间更新
    statusChanged = Signal(str)  # 当前日程状态变化
    entryChanged = Signal(dict)  # 当前 Entry 更新

    def __init__(self, app):
        super().__init__()
        self._runtime = app.runtime
        self._runtime.updated.connect(self._on_runtime_updated)
        self._runtime.currentsChanged.connect(lambda t: self.statusChanged.emit(t.value))

    # ------------------- 时间 -------------------
    @property
    def current_time(self) -> datetime:
        return self._runtime.current_time

    @property
    def current_day_of_week(self) -> int:
        return self._runtime.current_day_of_week

    @property
    def current_week(self) -> int:
        return self._runtime.current_week

    @property
    def current_week_of_cycle(self) -> int:
        return self._runtime.current_week_of_cycle

    @property
    def time_offset(self) -> int:
        return self._runtime.time_offset

    # ------------------- 日程 -------------------
    @property
    def schedule_meta(self) -> Optional[Dict]:
        if not self._runtime.schedule_meta:
            return None
        return self._runtime.schedule_meta.model_dump()

    @property
    def current_day_entries(self) -> List[Dict]:
        if not self._runtime.current_day:
            return []
        return [e.model_dump() for e in self._runtime.current_day.entries]

    @property
    def current_entry(self) -> Optional[Dict]:
        if not self._runtime.current_entry:
            return None
        return self._runtime.current_entry.model_dump()

    @property
    def next_entries(self) -> List[Dict]:
        if not self._runtime.next_entries:
            return []
        return [e.model_dump() for e in self._runtime.next_entries]

    @property
    def remaining_time(self) -> Dict:
        if not self._runtime.remaining_time:
            return {"minute": 0, "second": 0}
        r = self._runtime.remaining_time
        return {"minute": r.seconds // 60, "second": r.seconds % 60}

    @property
    def progress(self) -> float:
        return self._runtime.get_progress_percent() or 0.0

    @property
    def current_status(self) -> str:
        return self._runtime.current_status.value if self._runtime.current_status else EntryType.FREE.value

    @property
    def current_subject(self) -> Optional[Dict]:
        if not self._runtime.current_subject:
            return None
        return self._runtime.current_subject.model_dump()

    @property
    def current_title(self) -> Optional[str]:
        return self._runtime.current_title

    # ------------------- 内部事件 -------------------
    def _on_runtime_updated(self):
        self.updated.emit()
        self.entryChanged.emit(self.current_entry or {})


class ConfigAPI:
    def __init__(self, app):
        self._app = app

    def get(self) -> dict:
        return self._app.globalConfig


class AutomationAPI:
    def __init__(self, app):
        self._app = app

    def register(self, task):
        self._app.automation_manager.add_task(task)


class UiAPI(QObject):
    settingsPageRegistered = Signal()
    def __init__(self):
        super().__init__()
        self._registered_pages: list[dict] = []

    @property
    def pages(self):
        return self._registered_pages

    def register_settings_page(
        self,
        plugin,
        qml_path: str | Path,
        title: str | None = None,
        icon: str | None = None
    ):
        """插件提供相对路径，可自定义 title 和 icon"""
        qml_path = Path(qml_path)
        if not qml_path.is_absolute():
            qml_path = plugin.PATH / qml_path

        pid = plugin.meta.get("id")
        if not pid:
            raise ValueError("Plugin initialization failed, missing meta.id")

        self._registered_pages.append({
            "id": pid,
            "page": qml_path.resolve().as_uri(),
            "title": title or plugin.meta.get("name", "UNKNOWN"),
            "icon": icon or plugin.meta.get("icon", "ic_fluent_cube_20_regular")
        })
        self.settingsPageRegistered.emit()
        logger.debug(f"Plugin: {pid} register settings page: {qml_path}")


class PluginAPI:
    def __init__(self, app):
        self.widgets: WidgetsAPI = WidgetsAPI(app)
        self.notify: NotifyAPI = NotifyAPI(app)
        self.schedule: ScheduleAPI = ScheduleAPI(app)
        self.theme: ThemeAPI = ThemeAPI(app)
        self.runtime: RuntimeAPI = RuntimeAPI(app)
        self.config: ConfigAPI = ConfigAPI(app)
        self.automation: AutomationAPI = AutomationAPI(app)
        self.ui: UiAPI = UiAPI()


class CW2Plugin(QObject):
    def __init__(self, api: PluginAPI):
        super().__init__()
        self.PATH = Path()
        self.meta = {}
        self.api = api

    def on_load(self):
        pass

    def on_unload(self):
        pass
