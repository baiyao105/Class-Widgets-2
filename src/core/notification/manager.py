from typing import Dict

from PySide6.QtCore import Signal, QObject
from loguru import logger

from src.core.notification import NotificationData, NotificationLevel, NotificationProviderConfig


class NotificationManager(QObject):
    """
    统一通知出口
    """

    notified = Signal(dict)  # 给 QML 的 payload

    def __init__(self, config_manager):
        super().__init__()
        self.providers: Dict[str, object] = {}
        self.configs = config_manager

    def register_provider(self, provider):
        """
        注册 Provider，同时确保配置存在
        """
        self.providers[provider.id] = provider
        _ = provider.get_config()  # 自动创建默认配置

    def is_enabled(self, provider_id: str) -> bool:
        """
        检查某个 provider 是否被允许推送通知
        """
        cfg = self.configs.notifications.providers.get(provider_id)
        return True if cfg is None else cfg.enabled

    def dispatch(self, data: NotificationData, cfg=None):
        """
        最终分发点
        1. 检查 provider 是否启用
        2. 根据配置决定是否使用系统通知或自带铃声
        """
        # 如果没有 cfg，就用 configs 里存的配置
        if cfg is None:
            cfg = self.configs.notifications.providers.get(data.provider_id)
        if cfg is None:
            cfg = NotificationProviderConfig()

        # 检查是否启用
        if not getattr(cfg, "enabled", True):
            logger.debug(f"Notification blocked by config: {data.provider_id}")
            return

        payload = data.model_dump()
        payload["useSystem"] = getattr(cfg, "use_system_notify", False)
        payload["sound"] = getattr(cfg, "sound", None)

        self.notified.emit(payload)
        logger.info(f"Notification dispatched: {data.title} (Provider={data.provider_id})")

    def push_activity(self, status: str, subject: dict = None, title: str = None):
        """
        处理来自ScheduleRuntime的通知信号
        """
        try:
            # 确定通知级别和图标
            level = NotificationLevel.ANNOUNCEMENT
            icon = "ic_fluent_shifts_activity_20_filled"
            
            # 根据状态设置默认标题
            if not title:
                status_mapping = {
                    "class": "上课提醒",
                    "break": "课间休息",
                    "free": "自由时间",
                    "preparation": "预备铃",
                    "activity": "活动提醒"
                }
                title = status_mapping.get(status, f"状态变更: {status}")
            
            # 构建消息内容
            if subject and isinstance(subject, dict):
                subject_name = subject.get('name', '未知科目')
                message = f"当前: {subject_name}" if status == "class" else f"下一个: {subject_name}"
            else:
                message = f"状态变更为: {status}"
            
            # 创建通知数据
            data = NotificationData(
                provider_id="com.classwidgets.schedule.runtime",
                level=level,
                title=title,
                message=message,
                duration=5000,
                closable=True
            )
            
            self.dispatch(data)
            
        except Exception as e:
            logger.error(f"Failed to push activity notification: {e}")

    def push_plugin_notification(self, message: str, provider_id: str = "com.classwidgets.plugins"):
        """
        处理来自插件的通知
        """
        try:
            data = NotificationData(
                provider_id=provider_id,
                level=NotificationLevel.INFO,
                title="插件通知",
                message=message,
                duration=4000,
                closable=True
            )
            
            self.dispatch(data)
            
        except Exception as e:
            logger.error(f"Failed to push plugin notification: {e}")

    def push(self, icon: str, level: int, title: str, message: str = ""):
        """
        QML调试界面使用的通用推送方法
        """
        try:
            data = NotificationData(
                provider_id="com.classwidgets.debugger",
                level=level,
                title=title,
                message=message,
                duration=4000,
                closable=True
            )
            
            self.dispatch(data)
            
        except Exception as e:
            logger.error(f"Failed to push notification: {e}")
