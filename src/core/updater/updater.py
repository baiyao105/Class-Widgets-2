import os
import shutil
import subprocess
from pathlib import Path
import zipfile

from src import __app_filename__

ZIP_APP_NAME = "Class Widgets 2.exe"


class WindowsUpdater:
    """负责解压更新，并生成批处理脚本在程序退出后替换文件"""

    def __init__(self, temp_dir: Path, exe_name: str = __app_filename__):
        self.temp_dir = temp_dir
        self.exe_name = exe_name

    def apply_update(self, zip_path: Path, target_dir: Path):
        # 解压到临时目录
        extract_dir = self.temp_dir / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)

        old_exe = target_dir / self.exe_name
        new_exe = extract_dir / ZIP_APP_NAME

        # 生成批处理脚本：等待当前程序退出后再替换 exe 并启动
        cmd_file = self.temp_dir / "replace_and_restart.cmd"
        with open(cmd_file, "w", encoding="utf-8") as f:
            f.write(
                f"""
                @echo off
                timeout /t 2 /nobreak >nul
                echo Replacing files...
                xcopy /E /Y /Q "{extract_dir}" "{target_dir}"
                move /Y "{new_exe}" "{old_exe}"
                start "" "{old_exe}"
                """
            )

        # 启动批处理脚本，然后退出当前程序
        subprocess.Popen(["cmd", "/c", str(cmd_file)], close_fds=True)
        os._exit(0)
