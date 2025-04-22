#!/usr/bin/env bash
# run_ui.sh - 启动 UI 界面
# 加载 Sentaurus 环境和 Python 虚拟环境，然后启动图形界面

# 获取脚本所在目录路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 检查并加载 Sentaurus 环境
if [ -z "$STROOT" ] || [ -z "$STRELEASE" ]; then
    # 如果项目目录有sentaurus_env.sh，优先使用它
    if [ -f "${SCRIPT_DIR}/sentaurus_env.sh" ]; then
        echo "加载项目 Sentaurus 环境..."
        source "${SCRIPT_DIR}/sentaurus_env.sh"
    # 如果 Sentaurus 环境变量未设置，尝试加载系统环境
    elif [ -f /usr/local/synopsys/sentaurus/tcad/current/tcad.bash ]; then
        echo "加载系统 Sentaurus 环境..."
        source /usr/local/synopsys/sentaurus/tcad/current/tcad.bash
    elif [ -f $HOME/synopsys/sentaurus/tcad/current/tcad.bash ]; then
        echo "加载用户 Sentaurus 环境..."
        source $HOME/synopsys/sentaurus/tcad/current/tcad.bash
    else
        echo "警告: 无法找到 Sentaurus 环境文件，可能影响仿真功能"
    fi
fi

# 优先尝试使用 swb_env (与run_auto_sim.sh相同)
if [ -f "${SCRIPT_DIR}/swb_env/bin/activate" ]; then
    echo "激活 swb_env Python 虚拟环境..."
    source "${SCRIPT_DIR}/swb_env/bin/activate"
# 如果swb_env不存在，尝试使用.fs_auto_sim_env作为备用
elif [ -f "${SCRIPT_DIR}/.fs_auto_sim_env/bin/activate" ]; then
    echo "激活 .fs_auto_sim_env Python 虚拟环境..."
    source "${SCRIPT_DIR}/.fs_auto_sim_env/bin/activate"
else
    echo "错误: 无法找到 Python 虚拟环境，请确保已运行 setup_env.sh"
    exit 1
fi

# 设置 Python 模块搜索路径: 包含 auto_sim 和 auto_sim_tool
export PYTHONPATH="$SCRIPT_DIR/auto_sim:$SCRIPT_DIR/auto_sim_tool:$PYTHONPATH"

# 设置Python I/O编码为UTF-8，避免中文乱码
export PYTHONIOENCODING=UTF-8

echo "启动自动仿真界面..."
# 启动 PySide2 GUI
python "${SCRIPT_DIR}/auto_sim_tool/fs_auto_sim/pyside_gui.py" 