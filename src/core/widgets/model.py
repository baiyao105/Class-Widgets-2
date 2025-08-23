import uuid
from typing import List, Union, Dict
from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, QUrl, Signal, Property, Slot
from loguru import logger

class WidgetListModel(QAbstractListModel):
    InstanceIdRole = Qt.UserRole + 1
    TypeIdRole = Qt.UserRole + 2
    NameRole = Qt.UserRole + 3
    IconRole = Qt.UserRole + 4
    QmlPathRole = Qt.UserRole + 5
    BackendRole = Qt.UserRole + 6
    SettingsRole = Qt.UserRole + 7
    SettingsQmlRole = Qt.UserRole + 8

    modelChanged = Signal(str)
    definitonChanged = Signal(str)

    def __init__(self, app_central=None):
        super().__init__()
        self._app_central = app_central
        self._definitions: Dict[str, dict] = {}
        self._instances: List[dict] = []
        self._presets: Dict[str, List[Union[str, dict]]] = {}
        self._current_preset: str = ""

    def roleNames(self):
        return {
            self.InstanceIdRole: b"instanceId",
            self.TypeIdRole: b"typeId",
            self.NameRole: b"name",
            self.IconRole: b"icon",
            self.QmlPathRole: b"qmlPath",
            self.BackendRole: b"backendObj",
            self.SettingsRole: b"settings",
            self.SettingsQmlRole: b"settingsQml",
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._instances)

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self._instances):
            return None
        w = self._instances[index.row()]
        if role == self.InstanceIdRole:
            return w.get("instance_id", "")
        if role == self.TypeIdRole:
            return w.get("type_id", "")
        if role == self.NameRole:
            return w.get("name", "")
        if role == self.IconRole:
            return w.get("icon", "")
        if role == self.QmlPathRole:
            return w.get("qml_path", "")
        if role == self.BackendRole:
            return w.get("backend_obj", None)
        if role == self.SettingsRole:
            return w.get("settings", {})
        if role == self.SettingsQmlRole:
            return w.get("settings_qml", self._definitions.get(w.get("type_id", ""), {}).get("settings_qml", ""))
        return None

    def _normalize_preset_entries(self, entries: List[Union[str, dict]]) -> List[dict]:
        normalized = []
        for e in entries:
            if isinstance(e, str):
                normalized.append({"type_id": e, "instance_id": str(uuid.uuid4())})
            elif isinstance(e, dict):
                type_id = e.get("type_id")
                if not type_id:
                    continue
                inst_id = e.get("instance_id", str(uuid.uuid4()))
                normalized.append({"type_id": type_id, "instance_id": inst_id, "settings": e.get("settings", {})})
        return normalized

    def load_config(self):
        if not self._app_central:
            return
        raw_presets = self._app_central.get_config("preferences", "widgets_presets") or {}
        self._presets = {name: self._normalize_preset_entries(entries) for name, entries in raw_presets.items()}
        current_preset = self._app_central.get_config("preferences", "current_preset") or ""
        if current_preset:
            self.load_preset(current_preset)

    @Slot(str, list)
    def updatePreset(self, preset_name: str, enabled_entries: list):
        self._presets[preset_name] = self._normalize_preset_entries(enabled_entries)
        if self._current_preset == preset_name:
            self.load_preset(preset_name)
        self.modelChanged.emit("preset")

    @Slot(str, list)
    def set_preset(self, preset_name: str, entries: list):
        self._presets[preset_name] = self._normalize_preset_entries(entries)

    @Slot(str)
    def load_preset(self, preset_name: str):
        if preset_name not in self._presets:
            return
        entries = self._presets[preset_name]
        new_instances: List[dict] = []
        for entry in entries:
            type_id = entry.get("type_id")
            if not type_id or type_id not in self._definitions:
                continue
            definition = self._definitions[type_id]
            instance = dict(definition)
            instance["instance_id"] = entry.get("instance_id", str(uuid.uuid4()))
            instance["type_id"] = type_id
            instance["settings"] = entry.get("settings", definition.get("default_settings", {})) or {}
            if "backend_obj" in entry:
                instance["backend_obj"] = entry["backend_obj"]
            new_instances.append(instance)
        self.beginResetModel()
        self._instances = new_instances
        self._current_preset = preset_name
        self.endResetModel()
        self.modelChanged.emit("preset")

    def add_widget(self, widget_def: dict):
        type_id = widget_def.get("id")
        if not type_id or type_id in self._definitions:
            return
        qml_path = widget_def.get("qml_path", "")
        if qml_path:
            widget_def["qml_path"] = QUrl.fromLocalFile(qml_path).toString()
        settings_qml = widget_def.get("settings_qml", "")
        if settings_qml:
            widget_def["settings_qml"] = QUrl.fromLocalFile(settings_qml).toString()
        widget_def.setdefault("default_settings", {})
        self._definitions[type_id] = widget_def
        self.definitonChanged.emit(type_id)

    @Slot(str)
    def addInstance(self, type_id: str):
        if type_id not in self._definitions:
            return
        definition = self._definitions[type_id]
        instance = dict(definition)
        instance["instance_id"] = str(uuid.uuid4())
        instance["type_id"] = type_id
        instance["settings"] = dict(definition.get("default_settings", {}))
        if "backend_obj" in definition:
            instance["backend_obj"] = definition["backend_obj"]
        self.beginInsertRows(QModelIndex(), len(self._instances), len(self._instances))
        self._instances.append(instance)
        self.endInsertRows()
        self.modelChanged.emit("add")

    @Slot(int, int)
    def moveWidget(self, from_index: int, to_index: int):
        if from_index == to_index or from_index < 0 or to_index < 0 or from_index >= len(
                self._instances) or to_index >= len(self._instances):
            return
        self.beginMoveRows(QModelIndex(), from_index, from_index, QModelIndex(),
                           to_index if to_index < from_index else to_index + 1)
        w = self._instances.pop(from_index)
        self._instances.insert(to_index, w)
        self.endMoveRows()
        self.modelChanged.emit("reorder")

    @Slot(str)
    def removeWidget(self, instance_id: str):
        for i, w in enumerate(self._instances):
            if w.get("instance_id") == instance_id:
                self.beginRemoveRows(QModelIndex(), i, i)
                self._instances.pop(i)
                self.endRemoveRows()
                self.modelChanged.emit("remove")
                return

    @Slot(str, dict)
    def updateSettings(self, instance_id: str, settings: dict):
        for i, w in enumerate(self._instances):
            if w.get("instance_id") == instance_id:
                w_settings = w.get("settings", {})
                w_settings.update(settings)
                w["settings"] = w_settings
                ix = self.index(i)
                self.dataChanged.emit(ix, ix, [self.SettingsRole])
                return

    @Property(str, notify=modelChanged)
    def currentPreset(self):
        return self._current_preset

    @Property(dict, notify=modelChanged)
    def presets(self):
        return self._presets

    @Property(dict, notify=definitonChanged)
    def definitions(self):
        return self._definitions

    @Property('QVariantList', notify=definitonChanged)
    def definitionsList(self):
        return list(self._definitions.values())
