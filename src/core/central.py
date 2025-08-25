import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Property, Signal, Slot, QPoint
from PySide6.QtWidgets import QApplication
from RinUI import RinUIWindow
from loguru import logger

from src.core import CONFIGS_PATH, QML_PATH
from src.core.config import ConfigManager, RootConfig
from src.core.directories import PathManager, DEFAULT_THEME, CW_PATH
from src.core.models import ScheduleData, MetaInfo
from src.core.notification import Notification
from src.core.parser import ScheduleParser
from src.core.plugin.api import PluginAPI
from src.core.plugin.manager import PluginManager
from src.core.schedule import ScheduleRuntime
from src.core.schedule.editor import ScheduleEditor
from src.core.themes import ThemeManager
from src.core.timer import UnionUpdateTimer
from src.core.utils import generate_id, TrayIcon
from src.core.widgets import WidgetsWindow, WidgetListModel
from PySide6.QtQml import qmlRegisterSingletonInstance


class AppCentral(QObject):  # Class Widgets 的中枢
    updated = Signal()
    togglePanel = Signal(QPoint)
    widgetRegistered = Signal(str)  # 新增：widget注册信号

    def __init__(self):  # 初始化
        super().__init__()
        self._initialize_schedule_components()
        self._initialize_cores()
        self._initialize_ui_components()

    def _initialize_cores(self):
        """初始化核心"""
        self.app_instance = QApplication.instance()
        self.path_manager = PathManager()  # 统一路径管理
        self.configs = ConfigManager(path=CONFIGS_PATH, filename="configs.json")
        self.theme_manager = ThemeManager(self)
        self.widgets_model = WidgetListModel(self)
        self.plugin_api = PluginAPI(self)
        self.plugin_manager = PluginManager(self.plugin_api)
        
    def _initialize_schedule_components(self):
        """初始化调度相关组件"""
        self.current_schedule_path = None
        self.current_schedule_filename = None
        self.current_schedule_parser = None
        self.schedule: Optional[ScheduleData] = None
        
        self.union_update_timer = UnionUpdateTimer()
        self.runtime = ScheduleRuntime(self.schedule, self)
        self._notification = Notification()
        self._schedule_editor = None
        
    def _initialize_ui_components(self):
        """初始化UI组件"""
        self.settings = Settings(self)
        self.widgets_window = WidgetsWindow(self)  # 简化参数传递

    def run(self):  # 运行
        self._load_config()  # 加载配置
        self._load_schedule()  # 加载课程表
        self._load_runtime()  # 加载运行时
        self._init_tray_icon()  # 初始化托盘图标

        logger.info(f"Current schedule: {self.schedule.meta.id}")
        logger.info(f"Configs loaded.")
    
    def _load_config(self):
        """加载和验证配置"""
        self.configs.load_config()
        print(self.configs.app)

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
            current_schedule = self.get_config("schedule", "current_schedule") or "default"
            schedule_path = Path(CONFIGS_PATH / "schedules" / current_schedule).with_suffix(".json")
            self._schedule_editor = ScheduleEditor(schedule_path)
            self._schedule_editor.updated.connect(self.update)
        return self._schedule_editor

    @Property(dict, notify=updated)
    def globalConfig(self):  # 全局配置
        return self.config_manager.config

    @Slot()
    def quit(self):
        self.configs.save()
        self.cleanup()
        self.app_instance.quit()

    @Slot()
    def reloadSchedule(self):
        logger.info(f"Force Reload schedule: {self.current_schedule_filename}")
        self._load_schedule(force=True)

    # def register_widget(self, widget_id: str, name: str, qml_path: str, backend_obj: QObject = None, icon: str = None):
    #     """统一的widget注册接口"""
    #     widget_data = {
    #         "id": widget_id,
    #         "name": name,
    #         "icon": icon or "",
    #         "qml_path": qml_path,
    #         "backend_obj": backend_obj,
    #     }
    #     self.widgets_model.add_widget(widget_data)
    #     self.widgetRegistered.emit(widget_id)
    #     logger.debug(f"Widget registered: {widget_id}")
    
    def setup_qml_context(self, window):
        """
        为窗口设置标准的QML上下文属性
        
        Args:
            window: RinUIWindow实例
        """
        context = window.engine.rootContext()
        window.engine.addImportPath(QML_PATH)
        context.setContextProperty("WidgetsModel", self.widgets_model)
        context.setContextProperty("ThemeManager", self.theme_manager)
        context.setContextProperty("PluginManager", self.plugin_manager)
        context.setContextProperty("AppCentral", self)
        context.setContextProperty("PathManager", self.path_manager)

    # private methods
    def _load_schedule(self, force=False):  # 加载课程表
        path = self._get_schedule_path()
        
        if not self._should_reload_schedule(path, force):
            return
            
        self._update_schedule_path(path)
        self.schedule = self._parse_schedule_file()

    def _get_schedule_path(self) -> Path:
        """获取当前调度文件路径"""
        current_schedule = self.configs.schedule.current_schedule or "default"
        return Path(CONFIGS_PATH / "schedules" / current_schedule).with_suffix(".json")
    
    def _should_reload_schedule(self, path: Path, force: bool) -> bool:
        """判断是否需要重新加载调度"""
        return path != self.current_schedule_path or force
    
    def _update_schedule_path(self, path: Path):
        """更新调度路径信息"""
        self.current_schedule_path = path
        self.current_schedule_filename = path.name
        self.current_schedule_parser = ScheduleParser(path=path)
    
    def _parse_schedule_file(self) -> ScheduleData:
        """解析调度文件"""
        try:
            schedule = self.current_schedule_parser.load()
            logger.info(f"Loaded schedule: {self.current_schedule_path}")
            return schedule
        except FileNotFoundError:
            return self._create_default_schedule()
        except Exception as e:
            logger.error(f"Load schedule failed: {e}")
            return self._create_default_schedule()
    
    def _create_default_schedule(self) -> ScheduleData:
        """创建默认调度数据"""
        logger.warning("Schedule file not found, creating a new one...")
        schedule = ScheduleData(
            meta=MetaInfo(
                id=generate_id("meta"),
                version=1,
                maxWeekCycle=2,
                startDate=f"{datetime.now().year}-09-01"
            ),
            subjects=[],
            days=[]
        )
        self._save_schedule_file(schedule)
        return schedule
    
    def _save_schedule_file(self, schedule: ScheduleData):
        """保存课表文件"""
        self.current_schedule_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.current_schedule_path, "w", encoding="utf-8") as f:
                json.dump(asdict(schedule), f, ensure_ascii=False, indent=4)
            logger.info(f"Created new schedule file at {self.current_schedule_path}")
        except Exception as e:
            logger.error(f"Failed to create new schedule file: {e}")

    def _load_runtime(self):
        self._setup_runtime_connections()
        self._load_theme_and_plugins()
        self.widgets_window.run()
    
    def _setup_runtime_connections(self):
        """设置runtime连接"""
        self.runtime.update(self.schedule)
        self.runtime.notify.connect(self._notification.push_activity)
        self.union_update_timer.tick.connect(self.update)
        self.union_update_timer.start()  # 启动定时器 (interval=1000)
    
    def _load_theme_and_plugins(self):
        """主题和插件"""
        self.theme_manager.load()
        
        # 获取启用的插件列表
        enabled_plugins = self.configs.plugins.enabled or []
        self.plugin_manager.enabled_plugins = enabled_plugins
        
        # 加载插件（内置+外部）
        self.plugin_manager.load_all()

    def _init_tray_icon(self):
        self.tray_icon = TrayIcon(self)
        self.tray_icon.togglePanel.connect(self._on_tray_toggle)

    def _on_tray_toggle(self, pos: QPoint):
        self.togglePanel.emit(pos)

    # settings
    @Slot()
    def openSettings(self):
        """显示设置窗口"""
        if self.settings and self.settings.root_window:
            self.settings.root_window.show()
            self.settings.root_window.raise_()
            self.settings.root_window.requestActivate()
        else:
            logger.warning("Settings window not initialized correctly.")


class Settings(RinUIWindow):
    def __init__(self, parent: AppCentral):
        super().__init__()
        self.central = parent
        
        self.engine.addImportPath(DEFAULT_THEME)
        self.central.setup_qml_context(self)
        self.load(CW_PATH / "windows" / "Settings.qml")

