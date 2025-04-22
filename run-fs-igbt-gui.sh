#!/bin/bash
# FS-IGBT 全自动仿真 GUI 启动脚本 - 简化版

# 设置环境变量
export LANG=C
export PYTHONIOENCODING=UTF-8
export LC_ALL=C
export DISPLAY=:0
export QT_XKB_CONFIG_ROOT=/usr/share/X11/xkb
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_SCALE_FACTOR=1
export PYSIDE_GUI=1

# 进入项目目录
cd /home/tcad/STDB/MyProjects/AI_Lab/FS_IGBT

# 激活虚拟环境
source .fs_auto_sim_env/bin/activate

# 直接运行 PySide2 GUI (进入模拟模式)
echo "正在启动 FS-IGBT 图形界面 (模拟模式)..."
# 注意：使用短路运行方式，如果第一个命令失败，则运行第二个命令
python -c "import fs_auto_sim.pyside_gui; fs_auto_sim.pyside_gui.main_ui()" || python -m fs_auto_sim.console_ui 