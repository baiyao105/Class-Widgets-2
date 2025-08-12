from pathlib import Path

from loguru import logger

from .manager import ConfigManager, merge_config
from src.core import CONFIGS_PATH, QML_PATH

DEFAULT_CONFIG = {
    "schedule": {
        "current_schedule": "default",  # without suffix
        "preparation_time": 2,  # minutes
    },
    "preferences": {
        "current_theme": Path(QML_PATH / "widgets").as_uri(),
        "widgets": []
    },
    "plugins": {
        "enabled": []
    },
    "app": {
        "dev_mode": False,
        "no_logs": False,
        "version": "0.0.1",  # eg: 1.2.345
        "channel": "alpha"  # eg: alpha; beta; release
    }
}

global_config = ConfigManager(
    path=CONFIGS_PATH,
    filename="config.json"
)


def verify_config() -> bool:
    if global_config["app"]["version"] != DEFAULT_CONFIG["app"]["version"]:
        logger.warning("Config is outdated. Updating...")
        result = merge_config(
            target=global_config.config,
            source=DEFAULT_CONFIG
        )
        if result:
            global_config.config['app']['version'] = DEFAULT_CONFIG['app']['version']
            global_config.save_config()
        logger.info("Config updated.")
        return result
    logger.info("All configs updated.")
    return False
