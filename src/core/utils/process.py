import atexit
import os
import sys
import tempfile

from loguru import logger


def is_process_alive(pid: int) -> bool:
    """判断指定 PID 是否仍在运行"""
    try:
        os.kill(pid, 0)  # 不发送信号，只检测权限和存在性
    except ProcessLookupError:
        return False  # 进程不存在
    except PermissionError:
        return True   # 存在但无权限访问（仍在运行）
    else:
        return True


def ensure_single_instance():
    """确保程序单实例运行在 macOS"""
    if not (getattr(sys, "frozen", False) and sys.platform == "darwin"):
        logger.info("Not running in a frozen macOS app. Skipped single instance check.")
        return

    pid_file = os.path.join(tempfile.gettempdir(), "classwidgets2.pid")

    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as f:
                old_pid = int(f.read().strip())
            if is_process_alive(old_pid):
                logger.warning(f"Detected existing PID {old_pid}. Exiting duplicate instance.")
                sys.exit(0)
            else:
                # 残留文件，删除后重新创建
                logger.warning(f"Stale PID file found (PID {old_pid} not alive). Removing.")
                os.remove(pid_file)
        except Exception as e:
            logger.error(f"PID check failed: {e}")
            # 防止因文件损坏等原因卡死
            os.remove(pid_file)

    # 创建新的 PID 文件
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    def _cleanup_pid():
        try:
            if os.path.exists(pid_file):
                os.remove(pid_file)
        except Exception:
            pass

    atexit.register(_cleanup_pid)