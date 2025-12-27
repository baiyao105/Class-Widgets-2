import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from loguru import logger

from src.core.config import ConfigManager


class UpdateDownloader:
    def __init__(self, url: str, dest: Path, configs=ConfigManager):
        self.url = url
        self.dest = dest
        self._stop_flag = False  # 用于中断
        self.manual_stop = False  # 用于手动中断
        self.configs = configs

    def stop(self, manual=False):
        """外部调用停止下载"""
        self._stop_flag = True
        if manual:
            self.manual_stop = True

    def _resolve_url(self, url: str) -> str:
        """构造下载地址"""
        parsed = urlparse(url)
        if "github.com" not in parsed.netloc:
            return url

        if not (self.configs.network.mirror_enabled and self.configs.network.current_mirror):
            return url
        current = self.configs.network.current_mirror
        if current in ("auto", "自动选择"):
            return url
        mirror_netlocs = {urlparse(v).netloc for v in self.configs.network.mirrors.values() if v and v not in ("auto", "自动选择")}
        if parsed.netloc in mirror_netlocs:
            return url

        mirror_base = self.configs.network.mirrors.get(current)
        if not mirror_base:
            return url
        return f"{mirror_base}{url}"

    def _resolve_candidates(self, url: str) -> list:
        """生成候选下载地址列表"""
        parsed = urlparse(url)
        if "github.com" not in parsed.netloc or not self.configs.network.mirror_enabled:
            return [url]

        current = self.configs.network.current_mirror
        if current not in ("auto", "自动选择"):
            return [self._resolve_url(url)]
        mirrors = [v for k, v in self.configs.network.mirrors.items() if v and k not in ("auto", "自动选择")]
        candidates = [f"{m}{url}" for m in mirrors]
        candidates.append(url)  # 原始地址
        scored = []
        for u in candidates:
            latency = self._measure_latency(u)
            scored.append((u, latency if latency is not None else float("inf")))
        scored.sort(key=lambda x: x[1])  # 延迟从小到大
        return [u for u, _ in scored]

    def _measure_latency(self, url: str) -> float | None:
        """测量首字节延迟"""
        try:
            start = time.time()
            r = requests.get(url, stream=True, timeout=3)
            r.raise_for_status()
            r.close()
            return max(time.time() - start, 0.001)
        except Exception:
            return None


    def download(self, progress_callback=None) -> bool:
        """阻塞下载
        Args:
           progress_callback(None): 百分比, 速度

        Returns:
           bool: 是否成功下载"""
        self._stop_flag = False
        # 候选地址
        candidates = self._resolve_candidates(self.url)
        logger.info(f"Download candidates: {candidates}")
        for idx, resolved_url in enumerate(candidates):
            if self._stop_flag:
                return False
            try:
                logger.info(f"Trying to download from [{idx+1}/{len(candidates)}]: {resolved_url}")
                with requests.get(resolved_url, stream=True, timeout=15, proxies=None) as r:
                    r.raise_for_status()
                    total = int(r.headers.get('content-length', 0))
                    downloaded = 0
                    start_time = time.time()
                    with open(self.dest, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024 * 128):
                            if self._stop_flag:
                                return False
                            if not chunk:
                                continue
                            f.write(chunk)
                            downloaded += len(chunk)
                            elapsed = max(time.time() - start_time, 0.001)
                            speed = downloaded / elapsed  # bytes/sec
                            if progress_callback and total > 0:
                                progress_callback(downloaded / total * 100, speed)

                return True
            except Exception as e:
                logger.warning(f"Failed from {resolved_url}: {e}")
                continue

        return False
