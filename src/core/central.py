from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QCoreApplication, Property, Signal
from loguru import logger

from src.core import CONFIGS_PATH
from src.core.config import global_config, DEFAULT_CONFIG, verify_config
from src.core.models import ScheduleData
from src.core.parser import ScheduleParser
from src.core.schedule import ScheduleRuntime
from src.core.timer import UnionUpdateTimer


class AppCentral(QObject):  # Class Widgets 的中枢
    updated = Signal()

    def __init__(self):  # 初始化
        super().__init__()
        # variables
        self.current_schedule_path = None
        self.current_schedule_filename = None
        self.current_schedule_parser = None

        self.schedule: Optional[ScheduleData] = None

        # runtime
        self.app_instance = QCoreApplication.instance()
        self.union_update_timer = UnionUpdateTimer()
        self.runtime = ScheduleRuntime(self.schedule)

    def run(self):  # 运行
        global_config.load_config(DEFAULT_CONFIG)  # 加载配置
        verify_config()  # 验证配置

        self._load_schedule()  # 加载课程表
        self._load_runtime()  # 加载运行时

        logger.info(f"Current schedule: {self.schedule}")
        logger.info(f"Configs loaded.")

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

    @Property(dict, notify=updated)
    def globalConfig(self):  # 全局配置
        return global_config.config

    # private methods
    def _load_schedule(self):  # 加载课程表
        self.current_schedule_path = Path(
            CONFIGS_PATH / "schedules" / global_config["schedule"]["current_schedule"]
        ).with_suffix(".json")  # 获取路径
        self.current_schedule_filename = self.current_schedule_path.name

        self.current_schedule_parser = ScheduleParser(path=self.current_schedule_path)
        # 试解析
        try:
            self.schedule = self.current_schedule_parser.load()
        except FileNotFoundError:
            logger.warning("Schedule file not found, creating a new one...")
            # TODO: 创建新课表 / 错误处理
        except Exception as e:
            logger.error(f"Load schedule failed: {e}")

    def _load_runtime(self):
        self.runtime.update(self.schedule)
        self.union_update_timer.tick.connect(self.update)
        self.union_update_timer.start()  # 启动定时器 (interval=1000)
