from PySide6.QtCore import QObject

class CW2Plugin(QObject):
    """
    Class Widgets 2 插件基类
    插件写法推荐继承这个
    """
    def __init__(self, plugin_api):
        super().__init__()
        self.api = plugin_api  # 安全的插件API实例

    def on_load(self):
        """插件加载时调用"""
        pass

    def on_unload(self):
        """插件卸载时调用"""
        pass
