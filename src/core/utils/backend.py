from pathlib import Path

from PySide6.QtCore import Property, Slot, QObject, Signal
from PySide6.QtGui import QGuiApplication
from loguru import logger

from src.core.directories import LOGS_PATH, ROOT_PATH
from src.core.utils.auto_startup import autostart_supported, enable_autostart, disable_autostart, is_autostart_enabled


class UtilsBackend(QObject):
    initialized = Signal()
    logsUpdated = Signal()
    MAX_LOG_LINES = 200  # 最多保留200条日志

    def __init__(self):
        super().__init__()
        self._license_text = ""
        self._logs = []  # 内存存储日志
        self.load_license()
        logger.add(self._capture_log, level="DEBUG", enqueue=True)

    @Property("QVariantList", notify=logsUpdated)
    def logs(self):
        """暴露给 QML 的日志列表"""
        return self._logs

    def _capture_log(self, message):
        record = message.record
        log_entry = {
            "time": record["time"].strftime("%H:%M:%S"),
            "level": record["level"].name,
            "message": record["message"]
        }
        self._logs.append(log_entry)

        if len(self._logs) > self.MAX_LOG_LINES:
            self._logs.pop(0)

        self.logsUpdated.emit()


    @Property(str, notify=initialized)
    def licenseText(self):
        return self._license_text

    @Slot(result=list)
    def clearLogs(self):
        try:
            size = 0
            if LOGS_PATH.exists():
                for file in LOGS_PATH.glob("**/*"):
                    if file.is_file():
                        try:
                            file_size = file.stat().st_size / 1024 # kb
                            file.unlink()
                            size += file_size
                        except PermissionError:
                            logger.debug(f"Failed to delete {file.name} caused by permission error")
            return True, round(size, 2)
        except Exception as e:
            logger.exception(f"Failed to clear logs caused by {e}")
            return False, 0

    @Slot(str, result=bool)
    def copyToClipboard(self, text):
        try:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)
            return True
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            return False

    def load_license(self):
        try:
            with open(Path(ROOT_PATH / "LICENSE"), "r", encoding="utf-8") as f:
                license_text = f.read()
            self._license_text = license_text
        except Exception as e:
            logger.error(f"Failed to load license: {e}")

    # 自启动
    @Property(bool, constant=True)
    def autostartSupported(self):
        return autostart_supported()

    @Slot(bool, result=bool)
    def setAutostart(self, enabled):
        if enabled:
            enable_autostart()
        else:
            disable_autostart()

    @Slot(result=bool)
    def autostartEnabled(self):
        return autostart_supported() and is_autostart_enabled()
