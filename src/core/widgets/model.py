from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, QUrl


class WidgetListModel(QAbstractListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    IconRole = Qt.UserRole + 3
    QmlPathRole = Qt.UserRole + 4
    BackendRole = Qt.UserRole + 5

    def __init__(self):
        super().__init__()
        self._widgets = []

    def roleNames(self):
        return {
            self.IdRole: b"id",
            self.NameRole: b"name",
            self.IconRole: b"icon",
            self.QmlPathRole: b"qmlPath",
            self.BackendRole: b"backendObj",
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._widgets)

    def data(self, index, role):
        if not index.isValid():
            return None
        widget = self._widgets[index.row()]
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
        # qurl
        qml_path = widget_data.get("qml_path", "")
        if qml_path:
            qurl = QUrl.fromLocalFile(qml_path)
            widget_data["qml_path"] = qurl.toString()

        self.beginInsertRows(QModelIndex(), len(self._widgets), len(self._widgets))
        self._widgets.append(widget_data)
        self.endInsertRows()


    def clear_widgets(self):
        self.beginResetModel()
        self._widgets.clear()
        self.endResetModel()
