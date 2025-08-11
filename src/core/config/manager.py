import json
from pathlib import Path
from typing import Union, Optional, Dict, Any
from loguru import logger


def merge_config(target: Dict[str, Any], source: Dict[str, Any]) -> bool:
    """
    合并修改

    :param target: 本地配置
    :param source: 默认配置
    :return:
    """
    modified = False

    for key, value in source.items():
        if key not in target:
            target[key] = value
            modified = True
        elif isinstance(value, dict) and isinstance(target[key], dict):
            if merge_config(target[key], value):
                modified = True
    return modified


# 用了不知道多久的manager(?
class ConfigManager:
    def __init__(self, path: Union[str, Path], filename: str):
        """
        Json Config Manager

        :param path: json config file directory path
        :param filename: json config file name (e.g., rin_ui.json)
        """
        self.path = Path(path)
        self.filename = filename
        self.full_path = self.path / filename
        self.config = {}

    def load_config(self, default_config: Optional[dict] = None) -> dict:
        """
        Load config from file or initialize with default.

        :param default_config: default dict if file not exists or error
        :return: loaded or default config dict
        """
        if default_config is None:
            default_config = {}
        if self.full_path.exists():
            try:
                with open(self.full_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON解析错误: {e}. 使用默认配置.")
                self.config = default_config
            except Exception as e:
                logger.warning(f"读取配置文件时发生错误: {e}. 使用默认配置.")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()

        return self.config

    def update_config(self):
        """
        Update config with new config.
        :return:
        """
        try:
            with open(self.full_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f'更新配置失败: {e}')
            self.config = {}

    def update_values(self, key: Union[str, list], value) -> None:
        """
        Update config with new value.

        :param key: 单个键或键列表
        :param value: 要赋的值
        """
        if isinstance(key, str):
            self.config[key] = value
        elif isinstance(key, list):
            for k in key:
                self.config[k] = value
        else:
            raise TypeError('key 必须是 str 或 list')
        self.save_config()

    def save_config(self):
        """
        Save config to file.
        :return:
        """
        try:
            if not self.path.exists():
                self.path.mkdir(parents=True)
            with open(self.full_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f'保存配置失败: {e}')

    def get(self, *args, **kwargs):
        return self.config.get(*args, **kwargs)

    def __getitem__(self, key):
        return self.config.get(key)

    def __setitem__(self, key, value):
        self.config[key] = value
        self.save_config()

    def __repr__(self):
        return json.dumps(self.config, ensure_ascii=False, indent=4)
