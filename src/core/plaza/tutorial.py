import json
from collections.abc import Callable

from loguru import logger
from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from .bridge import DEFAULT_PLAZA_URL


class TutorialRecommendationsBridge(QObject):
    """Expose the small, curated Plugin Plaza list used by the first-run flow."""

    recommendationsChanged = Signal()
    loadingChanged = Signal()
    errorChanged = Signal()
    baseUrlChanged = Signal()

    _FALLBACK_RECOMMENDATIONS: list[dict] = []

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self._config_manager = config_manager
        self._base_url = self._read_base_url()
        self._recommendations = list(self._FALLBACK_RECOMMENDATIONS)
        self._loading = False
        self._error = ""
        self._shutting_down = False
        self._network_manager = QNetworkAccessManager(self)
        self._pending_replies: dict[QNetworkReply, Callable[[], None]] = {}

        if self._config_manager:
            self._config_manager.configChanged.connect(self._on_config_changed)

    def _read_base_url(self) -> str:
        configured_url = getattr(
            getattr(self._config_manager, "network", None), "plaza_url", ""
        )
        return (configured_url or DEFAULT_PLAZA_URL).rstrip("/")

    def _on_config_changed(self) -> None:
        base_url = self._read_base_url()
        if self._base_url != base_url:
            self._base_url = base_url
            self.baseUrlChanged.emit()

    @Property("QVariant", notify=recommendationsChanged)
    def recommendations(self) -> list[dict]:
        return self._recommendations

    @Property(bool, notify=loadingChanged)
    def loading(self) -> bool:
        return self._loading

    @Property(str, notify=errorChanged)
    def error(self) -> str:
        return self._error

    @Property(str, notify=baseUrlChanged)
    def baseUrl(self) -> str:
        return self._base_url

    def _set_loading(self, loading: bool) -> None:
        if self._loading != loading:
            self._loading = loading
            self.loadingChanged.emit()

    def _set_error(self, error: str) -> None:
        if self._error != error:
            self._error = error
            self.errorChanged.emit()

    def _track_reply(self, reply: QNetworkReply, callback: Callable[[], None]) -> None:
        self._pending_replies[reply] = callback
        reply.finished.connect(callback)

    def _take_reply(self, reply: QNetworkReply) -> bool:
        callback = self._pending_replies.pop(reply, None)
        if callback is None:
            return False
        try:
            reply.finished.disconnect(callback)
        except (RuntimeError, TypeError):
            pass
        return True

    @Slot()
    def fetchRecommendations(self) -> None:
        """Fetch the OOBE curation endpoint, keeping a local fallback on failure.

        The endpoint is owned by Plugin Plaza rather than the OOBE flow:
        ``GET /api/plugins/certified`` returns certified plugin manifests.
        """
        if self._shutting_down or self._loading:
            return

        self._set_loading(True)
        self._set_error("")
        request_url = QUrl(f"{self._base_url}/api/plugins/certified")
        request_url.setQuery(f"limit=6")
        request = QNetworkRequest(request_url)
        request.setTransferTimeout(10000)
        reply = self._network_manager.get(request)
        self._track_reply(reply, lambda: self._on_fetch_finished(reply))

    def _on_fetch_finished(self, reply: QNetworkReply) -> None:
        if not self._take_reply(reply):
            return
        self._set_loading(False)

        if self._shutting_down:
            reply.deleteLater()
            return

        try:
            if reply.error() != QNetworkReply.NoError:
                raise RuntimeError(reply.errorString())

            payload = json.loads(bytes(reply.readAll()).decode("utf-8"))
            plugins = payload.get("data", [])
            if not payload.get("ok") or not isinstance(plugins, list):
                raise ValueError("Invalid OOBE recommendation response")

            recommendations = []
            for item in plugins:
                if not isinstance(item, dict):
                    continue
                normalized_item = dict(item)
                normalized_item.setdefault("certified", True)
                recommendations.append(normalized_item)

            self._recommendations = recommendations
            self.recommendationsChanged.emit()
        except Exception as error:
            logger.warning("Unable to load tutorial plugin recommendations: {}", error)
            self._set_error(str(error))
        finally:
            reply.deleteLater()

    def shutdown(self) -> None:
        if self._shutting_down:
            return
        self._shutting_down = True
        for reply, callback in list(self._pending_replies.items()):
            try:
                reply.finished.disconnect(callback)
            except (RuntimeError, TypeError):
                pass
            if reply.isRunning():
                reply.abort()
            reply.deleteLater()
        self._pending_replies.clear()
        self._set_loading(False)
