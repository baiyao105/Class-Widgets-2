import importlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import List, Dict, Set
from loguru import logger

from src.core.directories import PLUGINS_PATH, BUILTIN_PLUGINS_PATH
from src.core.plugin import CW2Plugin


class PluginManager:
    def __init__(self, plugin_api):
        self.api = plugin_api
        self.plugins: Dict[str, CW2Plugin] = {}
        self.enabled_plugins = None

        self.external_path = PLUGINS_PATH
        self.builtin_path = BUILTIN_PLUGINS_PATH

    def set_enabled_plugins(self, enabled_plugins: List[str]):
        self.enabled_plugins = set(enabled_plugins)
        logger.debug(f"Enabled plugins: {enabled_plugins}")

    def discover_plugins_in_dir(self, base_dir: Path) -> List[Path]:
        """扫描指定目录下所有包含 cwplugin.json 的插件"""
        found = []
        if base_dir.exists() and base_dir.is_dir():
            for plugin_dir in base_dir.iterdir():
                if plugin_dir.is_dir() and (plugin_dir / "cwplugin.json").exists():
                    found.append(plugin_dir)
        return found

    def load_plugin_from_path(self, plugin_dir: Path, force=False):
        """
        Load Plugin from Path (Builtin / external)
        :param plugin_dir:
        :param force:
        :return:
        """
        try:
            meta_path = plugin_dir / "cwplugin.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))

            # 检查是否启用
            if meta["id"] not in self.enabled_plugins and not force:
                logger.info(f"Skipping disabled plugin {meta['id']}")
                return

            entry_file = plugin_dir / meta["entry"]
            if not entry_file.exists():
                raise FileNotFoundError(f"Entry file not found: {entry_file}")

            # 确保插件的目录在 sys.path 中（让插件内部 import 正常）
            sys.path.insert(0, str(plugin_dir))

            spec = importlib.util.spec_from_file_location(meta["id"], entry_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if not hasattr(module, "Plugin"):
                raise AttributeError("Plugin entry file does not define a 'Plugin' class")

            plugin_class = getattr(module, "Plugin")
            plugin_instance = plugin_class(self.api)

            if not isinstance(plugin_instance, CW2Plugin):
                raise TypeError("Plugin class must inherit from CW2Plugin")

            plugin_instance.on_load()
            self.plugins[meta["id"]] = plugin_instance

            logger.info(f"Loaded plugin {meta['name']} ({meta['id']}) v{meta['version']}")
        except Exception as e:
            logger.exception(f"Failed to load plugin from {plugin_dir}: {e}")

    def load_all(self, force=False):
        """扫描两个目录并加载所有启用的插件"""
        for plugin_dir in self.discover_plugins_in_dir(self.builtin_path):
            self.load_plugin_from_path(plugin_dir, force=force)

        for plugin_dir in self.discover_plugins_in_dir(self.external_path):
            self.load_plugin_from_path(plugin_dir, force=force)

    def unload_all(self):
        """卸载所有插件"""
        for name, plugin in list(self.plugins.items()):
            try:
                plugin.on_unload()
            except Exception as e:
                logger.error(f"Failed to unload plugin {name}: {e}")
        self.plugins.clear()
