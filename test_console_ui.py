#!/usr/bin/env python3
"""
测试 AI-Auto-TCAD 的命令行 UI 功能
"""

import os
import sys

# 确保能找到 fs_auto_sim 包
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 运行命令行 UI
from fs_auto_sim.console_ui import console_ui

if __name__ == "__main__":
    print("启动 AI-Auto-TCAD 命令行 UI 测试...")
    console_ui() 