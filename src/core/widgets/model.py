from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, QUrl, Signal, Property, Slot
from loguru import logger
from src.core.config import global_config


class WidgetListModel(QAbstractListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    IconRole = Qt.UserRole + 3
    QmlPathRole = Qt.UserRole + 4
    BackendRole = Qt.UserRole + 5

    # 合并信号：modelChanged，带一个str参数表示事件类型
    modelChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self._widgets = []         # All registered widgets
        self._widget_map = {}      # id -> widget_data quick lookup
        self._enabled_ids: list[str] = []  # Currently enabled widget IDs
        self._presets: dict = {}         # Presets: {preset_name: set_of_enabled_ids}
        self._current_preset = ""  # Currently selected preset name

    def load_config(self):
        self._presets = global_config.get("preferences").get("widgets_presets", {})
        self.switchPreset(global_config.get("preferences").get("current_preset", ""))
        logger.info("WidgetListModel Config loaded")

    def roleNames(self):
        return {
            self.IdRole: b"id",
            self.NameRole: b"name",
            self.IconRole: b"icon",
            self.QmlPathRole: b"qmlPath",
            self.BackendRole: b"backendObj",
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._enabled_ids)

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self._enabled_ids):
            return None

        widget_id = self._enabled_ids[index.row()]
        widget = self._widget_map.get(widget_id)
        if not widget:
            return None

        if role == self.IdRole:
            return widget["id"]
        if role == self.NameRole:
            return widget["name"]
        if role == self.IconRole:
            return widget["icon"]
        if role == self.QmlPathRole:
            return widget["qml_path"]
        if role == self.BackendRole:
            return widget["backend_obj"]
        return None

    def add_widget(self, widget_data: dict):
        widget_id = widget_data.get("id")
        if not widget_id:
            raise ValueError("widget_data must contain an 'id' field")

        qml_path = widget_data.get("qml_path", "")
        if qml_path:
            qurl = QUrl.fromLocalFile(qml_path)
            widget_data["qml_path"] = qurl.toString()

        if widget_id in self._widget_map:
            logger.warning(f"Widget '{widget_id}' already registered, skipped.")
            return

        self.beginResetModel()
        self._widgets.append(widget_data)
        self._widget_map[widget_id] = widget_data
        self.endResetModel()
        logger.debug(f"Registered widget {widget_id}")
        self.modelChanged.emit("widgets")  # 新增widget后通知

    def set_preset(self, preset_name: str, enabled_ids: set):
        self._presets[preset_name] = enabled_ids

    def load_preset(self, preset_name: str):
        if preset_name not in self._presets:
            logger.warning(f"Preset '{preset_name}' not found")
            return
        self.beginResetModel()
        self._enabled_ids = self._presets[preset_name].copy()
        self._current_preset = preset_name
        self.endResetModel()
        self.modelChanged.emit("preset")

    def current_preset(self):
        return self._current_preset

    def get_all_widgets(self):
        return self._widgets

    def get_enabled_widgets(self):
        return [w for w in self._widgets if w["id"] in self._enabled_ids]

    @Property(str, notify=modelChanged)
    def currentPreset(self):
        return self._current_preset

    @Property(dict, notify=modelChanged)
    def presets(self):
        return self._presets

    @Property(list, notify=modelChanged)
    def enabledWidgets(self):
        return list(self._enabled_ids)

    @Slot(str)
    def switchPreset(self, preset_name: str):
        """QML调用，切换预设"""
        self.load_preset(preset_name)
        self.modelChanged.emit(preset_name)

    @Slot(str, list)
    def updatePreset(self, preset_name: str, enabled_ids: list):
        """
        QML调用，覆盖指定预设的启用组件ID集合。
        enabled_ids 可以是QML传入的list<string>，这里转换为set处理。
        """
        if not isinstance(enabled_ids, (list, tuple)):
            logger.warning("update_preset: enabled_ids 参数类型错误，必须是列表或元组")
            return

        enabled_set = enabled_ids
        self._presets[preset_name] = enabled_set

        if self._current_preset == preset_name:
            self.load_preset(preset_name)
            # self.beginResetModel()
            # self._enabled_ids = enabled_set.copy()
            # self.endResetModel()
            # self.modelChanged.emit("enabled")

        logger.info(f"Preset '{preset_name}' updated with enabled widgets: {enabled_set}")