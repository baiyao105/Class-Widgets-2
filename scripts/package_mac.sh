#!/bin/bash
# 🔨 Build ClassWidgets-2 (macOS)

# 确保脚本在项目根目录执行
cd ..

# 使用 uv 执行 pyinstaller 打包
uv run pyinstaller --windowed \
  --icon "assets/images/logo.icns" \
  --add-data "src/qml:src/qml" \
  --add-data "src/plugins:src/plugins" \
  --add-data "assets:assets" \
  --add-data "LICENSE:." \
  --paths=. \
  --contents-directory . \
  --name="Class Widgets 2" \
  src/app.py
