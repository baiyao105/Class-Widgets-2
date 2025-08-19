import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Property, Signal, Slot, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QApplication, QMenu
from RinUI import RinUIWindow
from loguru import logger

from src.core import CONFIGS_PATH, QML_PATH
from src.core.config import global_config, DEFAULT_CONFIG, verify_config
from src.core.directories import PLUGINS_PATH, ASSETS_PATH
from src.core.models import ScheduleData, MetaInfo
from src.core.notification import Notification
from src.core.parser import ScheduleParser
from src.core.plugin.api import PluginAPI
from src.core.plugin.manager import PluginManager
from src.core.schedule import ScheduleRuntime
from src.core.schedule.editor import ScheduleEditor
from src.core.themes import ThemeManager
from src.core.timer import UnionUpdateTimer
from src.core.utils import generate_id, to_dict, TrayIcon
from src.core.widgets import WidgetsWindow


class AppCentral(QObject):  # Class Widgets 的中枢
    updated = Signal()
    togglePanel = Signal(QPoint)

    def __init__(self):  # 初始化
        super().__init__()
        # variables
        self.current_schedule_path = None
        self.current_schedule_filename = None
        self.current_schedule_parser = None

        self.schedule: Optional[ScheduleData] = None

        # runtime
        self.app_instance = QApplication.instance()
        self.union_update_timer = UnionUpdateTimer()
        self.runtime = ScheduleRuntime(self.schedule)
        self._notification = Notification()
        self._schedule_editor = None
        self.theme_manager = ThemeManager()
        self.plugin_api = PluginAPI(self)
        self.plugin_manager = PluginManager(self.plugin_api)

        # app
        self.settings = Settings()

        # widgets
        self.widgets_window = WidgetsWindow(
            theme_manager=self.theme_manager,
            plugin_manager=self.plugin_manager,
            app_central=self,
        )

    def run(self):  # 运行
        global_config.load_config(DEFAULT_CONFIG)  # 加载配置
        verify_config()  # 验证配置

        self._load_schedule()  # 加载课程表
        self._load_runtime()  # 加载运行时
        self._init_tray_icon()  # 初始化托盘图标

        logger.info(f"Current schedule: {self.schedule.meta.id}")
        logger.info(f"Configs loaded.")

    def update(self):  # 更新
        self._load_schedule()

        # 更新数据
        self.runtime.update(self.schedule)
        self.updated.emit()  # 发送信号

    def cleanup(self):
        self.union_update_timer.stop()
        logger.info("Clean up.")

    # for qml
    @Property(QObject, notify=updated)
    def scheduleRuntime(self):  # 运行时
        return self.runtime

    @Property(QObject, notify=updated)
    def notification(self):
        return self._notification

    @Property(QObject, notify=updated)
    def scheduleEditor(self):  # 课程表编辑器
        if not self._schedule_editor:
            schedule_path = Path(CONFIGS_PATH / "schedules" / global_config["schedule"]["current_schedule"]).with_suffix(".json")
            self._schedule_editor = ScheduleEditor(schedule_path)
            self._schedule_editor.updated.connect(self.update)
        return self._schedule_editor

    @Property(dict, notify=updated)
    def globalConfig(self):  # 全局配置
        return global_config.config

    @Slot()
    def reloadSchedule(self):
        logger.info(f"Force Reload schedule: {self.current_schedule_filename}")
        self._load_schedule(force=True)


    # private methods
    def _load_schedule(self, force=False):  # 加载课程表
        path = Path(CONFIGS_PATH / "schedules" / global_config["schedule"]["current_schedule"]).with_suffix(".json")

        if path != self.current_schedule_path or force:
            self.current_schedule_path = path  # 获取路径
            self.current_schedule_filename = self.current_schedule_path.name

            self.current_schedule_parser = ScheduleParser(path=self.current_schedule_path)
            # 试解析
            try:
                self.schedule = self.current_schedule_parser.load()
                logger.info(f"Loaded schedule: {self.current_schedule_path}")
            except FileNotFoundError:
                logger.warning("Schedule file not found, creating a new one...")
                self.schedule = ScheduleData(
                    meta=MetaInfo(
                        id=generate_id("meta"),
                        version=1,
                        maxWeekCycle=2,
                        startDate=f"{datetime.now().year}-09-01"
                    ),
                    subjects=[],
                    days=[]
                )
                # 保存到文件
                self.current_schedule_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    with open(self.current_schedule_path, "w", encoding="utf-8") as f:
                        json.dump(to_dict(self.schedule), f, ensure_ascii=False, indent=4)
                    logger.info(f"Created new schedule file at {self.current_schedule_path}")
                except Exception as e:
                    logger.error(f"Failed to create new schedule file: {e}")
            except Exception as e:
                logger.error(f"Load schedule failed: {e}")

    def _load_runtime(self):
        self.runtime.update(self.schedule)
        self.runtime.notify.connect(self._notification.push_activity)
        self.union_update_timer.tick.connect(self.update)
        self.union_update_timer.start()  # 启动定时器 (interval=1000)

        self.theme_manager.load()

        # 添加外部插件路径
        self.plugin_manager.enabled_plugins = global_config.get("plugins").get("enabled")

        # 加载插件（内置+外部）
        self.plugin_manager.load_all()
        self.widgets_window.run()

    def _init_tray_icon(self):
        self.tray_icon = TrayIcon(self)
        self.tray_icon.togglePanel.connect(self._on_tray_toggle)

    def _on_tray_toggle(self, pos: QPoint):
        self.togglePanel.emit(pos)


class Settings(RinUIWindow):
    def __init__(self):
        super().__init__()

        self.load(QML_PATH / "windows" / "Settings.qml")

