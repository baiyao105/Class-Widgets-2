from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QSortFilterProxyModel


class LogListModel(QAbstractListModel):
    """QML-friendly log model.

    暴露给 QML 的角色:
        - time:    日志时间字符串 (HH:MM:SS)
        - level:   日志级别 (DEBUG/INFO/WARNING/ERROR/SUCCESS)
        - message: 日志正文

    使用 QAbstractListModel 而不是 QVariantList, 这样 ListView 在新日志到达时
    会收到 rowsInserted 信号, 不会重置 contentY, 滚动位置/可见性得以保留。
    """

    TimeRole = Qt.UserRole + 1
    LevelRole = Qt.UserRole + 2
    MessageRole = Qt.UserRole + 3

    MAX_LOG_LINES = 200

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries: list[dict] = []

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._entries)

    def roleNames(self):
        return {
            self.TimeRole: b"time",
            self.LevelRole: b"level",
            self.MessageRole: b"message",
        }

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        if row < 0 or row >= len(self._entries):
            return None
        entry = self._entries[row]
        if role == self.TimeRole:
            return entry.get("time", "")
        if role == self.LevelRole:
            return entry.get("level", "")
        if role == self.MessageRole:
            return entry.get("message", "")
        return None

    def append_entry(self, entry: dict) -> None:
        """追加一条日志。在末尾若超出容量, 先移除最旧一条再追加。

        必须在 GUI 线程调用, 因为内部会触发 beginInsertRows/endInsertRows。
        """
        if len(self._entries) >= self.MAX_LOG_LINES:
            self.beginRemoveRows(QModelIndex(), 0, 0)
            self._entries.pop(0)
            self.endRemoveRows()

        new_index = len(self._entries)
        self.beginInsertRows(QModelIndex(), new_index, new_index)
        self._entries.append(entry)
        self.endInsertRows()

    def snapshot(self, limit: int = MAX_LOG_LINES) -> list[dict]:
        """返回最近 limit 条日志的浅拷贝 (list[dict])。"""
        safe_limit = max(0, min(limit, self.MAX_LOG_LINES))
        if safe_limit == 0:
            return []
        return [dict(item) for item in self._entries[-safe_limit:]]

    def clear(self) -> None:
        if not self._entries:
            return
        self.beginResetModel()
        self._entries.clear()
        self.endResetModel()


class LogFilterProxyModel(QSortFilterProxyModel):
    """对 LogListModel 做客户端过滤。

    支持两种过滤维度（可叠加）:
        - filter_text:  不区分大小写的子串匹配, 命中 time/level/message 任一即保留
        - filter_level: 精确级别匹配 (DEBUG/INFO/WARNING/ERROR/SUCCESS),
                        空串表示不过滤级别
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter_text: str = ""
        self._filter_level: str = ""

    def set_filter_text(self, text: str) -> None:
        self._filter_text = (text or "").lower()
        self.invalidateFilter()

    def set_filter_level(self, level: str) -> None:
        self._filter_level = level or ""
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        source = self.sourceModel()
        if source is None:
            return True
        index = source.index(source_row, 0, source_parent)
        if not index.isValid():
            return True

        time = source.data(index, LogListModel.TimeRole) or ""
        level = source.data(index, LogListModel.LevelRole) or ""
        message = source.data(index, LogListModel.MessageRole) or ""

        if self._filter_level and level != self._filter_level:
            return False

        if self._filter_text:
            haystack = f"{time} {level} {message}".lower()
            if self._filter_text not in haystack:
                return False

        return True
