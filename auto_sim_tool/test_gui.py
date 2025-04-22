#!/usr/bin/env python3
"""
测试 AI-Auto-TCAD 的 GUI 功能
注意：这个脚本是简化版的，仅用于测试界面布局和交互
"""

import os
import sys

# 确保能找到 fs_auto_sim 包
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 运行 GUI
from fs_auto_sim.gui import main_ui

if __name__ == "__main__":
    # 检查是否已安装 PySimpleGUI
    try:
        import PySimpleGUI
    except ImportError:
        print("需要安装 PySimpleGUI 才能运行界面。")
        print("请运行: pip install PySimpleGUI")
        sys.exit(1)
    
    print("启动 AI-Auto-TCAD GUI 测试...")
    main_ui() 