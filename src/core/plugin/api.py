from PySide6.QtCore import QObject, Signal

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

    # ================== 对外 API ==================

    # 注册小组件
    def register_widget(self, widget_id: str, name: str, qml_path: str, backend_obj: QObject = None, icon: str = None):
        self._app.widgets_window.register_widget(widget_id, name, qml_path, backend_obj, icon)

    # 获取当前课表数据
    def get_schedule(self):
        return self._app.schedule

    # 发通知
    def push_notification(self, message: str):
        self._app.notification.push_activity(message)

    # 获取当前主题
    def get_theme(self):
        return self._app.theme_manager.current_theme

    # 设置主题
    def set_theme(self, theme_name: str):
        self._app.theme_manager.set_theme(theme_name)

    # 获取配置
    def get_config(self):
        return self._app.globalConfig

    # 更新课表
    def reload_schedule(self):
        self._app.reloadSchedule()
