from loguru import logger

from .manager import ConfigManager, merge_config
from src.core import CONFIGS_PATH

DEFAULT_CONFIG = {
    "schedule": {
        "current_schedule": "default",  # without suffix
    },
    "app": {
        "dev_mode": False,
        "no_logs": False,
        "version": "0.0.1-alpha",
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
        logger.info("Config updated.")
        return result
    return False
