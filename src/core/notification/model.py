from enum import IntEnum
from typing import Optional
from pydantic import BaseModel


class NotificationLevel(IntEnum):
    INFO = 0          # 普通提示
    ANNOUNCEMENT = 1  # 上下课 / 状态
    WARNING = 2       # 更新 / 风险
    SYSTEM = 3        # 内部


class NotificationData(BaseModel):
    provider_id: str          # 来源 Provider ID
    level: int                # 实际由前端映射样式
    title: str
    message: Optional[str] = None

    # 行为 & 展示
    duration: int = 4000      # ms，0 = 常驻
    closable: bool = True
    silent: bool = False      # 是否无声音
    use_system: bool = False # 系统通知 or 应用内

    # 扩展字段（给灵动岛留口子）
    extra: dict = {}

class NotificationProviderConfig(BaseModel):
    enabled: bool = True
    use_system_notify: bool = False
    sound: Optional[str] = None
