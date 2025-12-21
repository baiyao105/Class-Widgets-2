from PySide6.QtCore import QObject, Slot
from typing import Optional
from .model import NotificationData, NotificationLevel, NotificationProviderConfig

class NotificationProvider(QObject):
    """
    一个 Provider = 一个通知来源（模块 / 插件）
    """

    def __init__(
        self,
        id: str,
        name: str,
        icon: Optional[str] = None,
        manager=None,  # 默认 None，内部会自动获取
    ):
        super().__init__()
        self.id = id
        self.name = name
        self.icon = icon

        # 自动获取 manager（如果没传，则尝试从 AppCentral.notification）
        if manager is None:
            from src.core import AppCentral
            self.manager = AppCentral.instance().notification  # 假设 AppCentral 提供 instance()
        else:
            self.manager = manager

        # 自动注册
        self.manager.register_provider(self)

    # ---------- config ----------
    def get_config(self) -> NotificationProviderConfig:
        """
        从 ConfigManager 读取该 provider 的配置
        """
        cfg = getattr(self.manager.configs.notifications, self.id, None)
        if cfg is None:
            return NotificationProviderConfig()
        return cfg

    @Slot(int, str, str, int, bool, result=None)  # QML 调用签名: level, title, message, duration, closable
    def push(
            self,
            level: int,
            title: str,
            message: Optional[str],
            duration: int,
            closable: bool,
    ):
        cfg = self.get_config()
        if not cfg.enabled:
            return

        data = NotificationData(
            provider_id=self.id,
            level=level,
            title=title,
            message=message,
            duration=duration,
            closable=closable,
        )

        self.manager.dispatch(data, cfg)