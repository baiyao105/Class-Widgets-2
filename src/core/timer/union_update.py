from PySide6.QtCore import QObject, QTimer, Signal
from datetime import datetime, timedelta


# 统一更新定时器

class UnionUpdateTimer(QObject):
    tick = Signal()  # 每秒对齐 tick 一次

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)

    def start(self):
        self._align_and_start()

    def stop(self):
        self._timer.stop()

    def _on_timeout(self):
        self.tick.emit()
        self._align_and_start()

    def _align_and_start(self):
        now = datetime.now()
        passed_ms = now.microsecond // 1000
        delay_ms = 1000 - passed_ms
        if delay_ms < 5:
            delay_ms += 1000
        self._timer.start(delay_ms)
