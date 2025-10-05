from PySide6.QtCore import QObject, Signal

from .base import AutomationTask
from .auto_hide import AutoHideTask


class AutomationManager(QObject):
    updated = Signal()

    def __init__(self, app_central):
        super().__init__()
        self.app_central = app_central
        self.tasks: list[AutomationTask] = []

        # 注册任务
        self.auto_hide_task = AutoHideTask(app_central)
        self.tasks.append(self.auto_hide_task)

    def update(self):
        for task in self.tasks:
            task.update()
        self.updated.emit()
