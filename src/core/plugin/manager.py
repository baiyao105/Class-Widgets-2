import importlib.util
import json
from pathlib import Path
from typing import List, Dict

from loguru import logger

from src.core.directories import PLUGINS_PATH
from .base import CW2Plugin


class PluginManager:
    def __init__(self, plugin_api):
        self.api = plugin_api
        self.plugins: Dict[str, CW2Plugin] = {}
        self.search_paths: List[Path] = []

    def add_search_path(self, path: Path):
        if path.exists() and path.is_dir():
            self.search_paths.append(path)

    def discover_plugins(self) -> List[Path]:
        found = []
        for path in self.search_paths:
            for plugin_dir in path.iterdir():
                if plugin_dir.is_dir() and (plugin_dir / "cwplugin.json").exists():
                    found.append(plugin_dir)
        return found

    def load_plugin(self, plugin_dir: Path):
        try:
            meta_path = plugin_dir / "plugin.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))

            module_name = meta["entry"]  # 一般是 "__init__"
            class_name = meta["class"]
            plugin_module_path = f"{plugin_dir.name}.{module_name}"

            module = importlib.import_module(plugin_module_path)
            plugin_class = getattr(module, class_name)
            plugin_instance = plugin_class(self.api)
            plugin_instance.on_load()

            self.plugins[meta["name"]] = plugin_instance
            logger.info(f"[插件系统] 加载插件 {meta['name']} v{meta['version']}")

        except Exception as e:
            logger.error(f"[插件系统] 加载插件失败 {plugin_dir}: {e}")

    def load_all(self):
        for plugin_dir in self.discover_plugins():
            self.load_plugin(plugin_dir)

    def unload_all(self):
        for name, plugin in self.plugins.items():
            try:
                plugin.on_unload()
            except Exception as e:
                logger.error(f"[插件系统] 卸载插件失败 {name}: {e}")
        self.plugins.clear()