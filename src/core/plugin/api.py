from datetime import datetime

from PySide6.QtCore import QObject, Signal
from typing import List, Optional

class PluginAPI(QObject):
    """
    安全的插件 API 层
    暴露给插件的所有功能都通过这里
    """

    # 可以定义插件可监听的全局信号
    scheduleUpdated = Signal()       # 课表更新
    themeChanged = Signal(str)       # 主题变化
    notify = Signal(str, int, str, str)  # icon, level, title, message # 通知被推送

    def __init__(self, app_central):
        super().__init__()
        self._app = app_central

        # 转接 AppCentral 的信号
        self._app.updated.connect(self.scheduleUpdated.emit)
        self._app.theme_manager.themeChanged.connect(self.themeChanged.emit)
        self._app.notification.notify.connect(self.notify.emit)

        # self._runtime = self._app.schedule_runtime

    # ================== 对外 API ==================

    ### 控制
    # 注册小组件
    def register_widget(
            self, widget_id: str, name: str, qml_path: str,
            backend_obj: QObject = None, icon: str = None
    ):
        """通过AppCentral统一注册widget"""
        self._app.register_widget(widget_id, name, qml_path, backend_obj, icon)

    # 发通知
    def push_notification(self, message: str):
        self._app.notification.push_activity(message)

    ### 获取
    # 课表
    def get_schedule(self):
        return self._app.schedule

    @property
    def runtime(self):
        return self._runtime

    def get_datetime(self) -> datetime:
        return self._app.runtime.current_time

    # 获取当前主题
    def get_theme(self) -> Optional[str]:
        return self._app.theme_manager.current_theme

    # 获取配置
    def get_config(self) -> Optional[dict]:
        return self._app.globalConfig

    # 更新课表
    def reload_schedule(self):
        self._app.reloadSchedule()


class CW2Plugin(QObject):
    """
    Class Widgets 2 插件基类
    插件写法推荐继承这个
    """
    def __init__(self, plugin_api: PluginAPI):
        super().__init__()
        self.api = plugin_api  # 插件API实例

    def on_load(self):
        """插件加载时调用"""
        pass

    def on_unload(self):
        """插件卸载时调用"""
        pass

