import importlib.util
import json
import sys
from pathlib import Path
from typing import List, Dict

from loguru import logger

from src.core.directories import PLUGINS_PATH
from .base import CW2Plugin


import importlib
import importlib.util
import json
import sys
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
        self.builtin_plugins: List[str] = []  # list of built-in plugin module paths

    # ===== External plugins =====
    def add_search_path(self, path: Path):
        """Add a directory to the external plugin search paths."""
        if path.exists() and path.is_dir():
            self.search_paths.append(path)

    def discover_plugins(self) -> List[Path]:
        """Find all directories containing cwplugin.json in search paths."""
        found = []
        for path in self.search_paths:
            for plugin_dir in path.iterdir():
                if plugin_dir.is_dir() and (plugin_dir / "cwplugin.json").exists():
                    found.append(plugin_dir)
        return found

    def load_plugin_from_path(self, plugin_dir: Path):
        """Load a plugin from a directory on disk."""
        try:
            meta_path = plugin_dir / "cwplugin.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))

            entry_file = plugin_dir / meta["entry"]
            if not entry_file.exists():
                raise FileNotFoundError(f"Entry file not found: {entry_file}")

            # Add plugin dir to sys.path so relative imports inside plugin work
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

            logger.info(f" Loaded plugin {meta['name']} ({meta['id']}) v{meta['version']}")
        except Exception as e:
            logger.exception(f" Failed to load plugin from {plugin_dir}: {e}")

    # ===== Built-in plugins =====
    def add_builtin_plugin(self, module_path: str):
        """Register a built-in plugin by its module path (e.g. 'src.plugins.myplugin')."""
        self.builtin_plugins.append(module_path)

    def load_builtin_plugin(self, module_path: str):
        """Load a built-in plugin by import."""
        try:
            module = importlib.import_module(module_path)

            if not hasattr(module, "Plugin"):
                raise AttributeError("Built-in plugin does not define a 'Plugin' class")

            plugin_class = getattr(module, "Plugin")
            plugin_instance = plugin_class(self.api)

            if not isinstance(plugin_instance, CW2Plugin):
                raise TypeError("Built-in plugin class must inherit from CW2Plugin")

            plugin_instance.on_load()
            self.plugins[module_path] = plugin_instance

            logger.info(f" Loaded built-in plugin {module_path}")
        except Exception as e:
            logger.exception(f" Failed to load built-in plugin {module_path}: {e}")

    # ===== Unified API =====
    def load_all(self):
        """Load all external and built-in plugins."""
        # External
        for plugin_dir in self.discover_plugins():
            self.load_plugin_from_path(plugin_dir)

        # Built-in
        for module_path in self.builtin_plugins:
            self.load_builtin_plugin(module_path)

    def unload_all(self):
        """Unload all loaded plugins."""
        for name, plugin in list(self.plugins.items()):
            try:
                plugin.on_unload()
            except Exception as e:
                logger.error(f" Failed to unload plugin {name}: {e}")
        self.plugins.clear()
