from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable

import requests


class PluginDownloadCancelled(Exception):
    """Raised when a plugin download is cancelled by the user."""


class PluginDownloadPaused(Exception):
    """Raised when a plugin download is paused and can be resumed later."""


class PluginDownloader:
    """Stream one remote plugin archive to a local file."""

    def __init__(self, url: str, destination: Path, *, max_size: int = 100 * 1024 * 1024):
        self.url = url
        self.destination = Path(destination)
        self.max_size = max_size
        self._cancel_event = threading.Event()
        self._pause_event = threading.Event()
        self._response: requests.Response | None = None
        self._response_lock = threading.Lock()

    def cancel(self) -> None:
        self._cancel_event.set()
        self._interrupt_response()

    def pause(self) -> None:
        self._pause_event.set()
        self._interrupt_response()

    def download(
        self,
        progress_callback: Callable[[float, float, int, int], None] | None = None,
    ) -> Path:
        if self._cancel_event.is_set():
            raise PluginDownloadCancelled()
        if self._pause_event.is_set():
            raise PluginDownloadPaused()

        self.destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.destination.with_name(f".{self.destination.name}.part")
        resumed_bytes = temporary.stat().st_size if temporary.exists() else 0
        if resumed_bytes > self.max_size:
            temporary.unlink(missing_ok=True)
            raise ValueError("Plugin download is too large.")

        headers = {"Range": f"bytes={resumed_bytes}-"} if resumed_bytes else {}

        try:
            with requests.get(
                self.url,
                stream=True,
                timeout=(10, 60),
                allow_redirects=True,
                headers=headers,
            ) as response:
                self._set_response(response)
                self._raise_if_interrupted()
                response.raise_for_status()
                content_length = int(response.headers.get("content-length", "0") or 0)
                is_resuming = resumed_bytes > 0 and response.status_code == 206
                downloaded = resumed_bytes if is_resuming else 0
                mode = "ab" if is_resuming else "wb"
                total_bytes = self._total_bytes(response, content_length, downloaded)
                if total_bytes > self.max_size:
                    raise ValueError("Plugin download is too large.")

                started_at = time.monotonic()
                with temporary.open(mode) as output:
                    for chunk in response.iter_content(chunk_size=1024 * 32):
                        self._raise_if_interrupted()
                        if not chunk:
                            continue
                        downloaded += len(chunk)
                        if downloaded > self.max_size:
                            raise ValueError("Plugin download is too large.")
                        output.write(chunk)
                        if progress_callback:
                            elapsed = max(time.monotonic() - started_at, 0.001)
                            speed = (downloaded - resumed_bytes) / elapsed
                            percent = downloaded / total_bytes * 100 if total_bytes else 0.0
                            progress_callback(percent, speed, downloaded, total_bytes)

            temporary.replace(self.destination)
            if progress_callback:
                progress_callback(100.0, 0.0, downloaded, total_bytes or downloaded)
            return self.destination
        except (PluginDownloadPaused, PluginDownloadCancelled):
            raise
        except Exception:
            self._raise_if_interrupted()
            temporary.unlink(missing_ok=True)
            raise
        finally:
            self._set_response(None)

    def _raise_if_interrupted(self) -> None:
        if self._cancel_event.is_set():
            raise PluginDownloadCancelled()
        if self._pause_event.is_set():
            raise PluginDownloadPaused()

    def _interrupt_response(self) -> None:
        with self._response_lock:
            response = self._response
        if response is not None:
            response.close()

    def _set_response(self, response: requests.Response | None) -> None:
        with self._response_lock:
            self._response = response

    @staticmethod
    def _total_bytes(response: requests.Response, content_length: int, downloaded: int) -> int:
        content_range = response.headers.get("content-range", "")
        if "/" in content_range:
            total = content_range.rsplit("/", 1)[-1]
            if total.isdigit():
                return int(total)
        return downloaded + content_length
