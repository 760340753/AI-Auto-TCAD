#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "设置环境..."
# 如果存在Sentaurus环境设置脚本，则加载它
if [ -f "${SCRIPT_DIR}/sentaurus_env.sh" ]; then
    source "${SCRIPT_DIR}/sentaurus_env.sh"
fi

# 激活Python虚拟环境
source "${SCRIPT_DIR}/swb_env/bin/activate"

# 强制设置Python I/O编码为UTF-8
export PYTHONIOENCODING=UTF-8

echo "环境准备就绪。运行全自动仿真脚本..."
cd "${SCRIPT_DIR}"

# 运行主脚本，传递API密钥并禁用模拟模式
echo "运行全自动仿真脚本..."
python auto_sim/auto_sim_main.py --api-key sk-buspthftjrkhcudljfardlbubjlmpfoxehgstdipajrxpccc
# 注意：移除了 --fake-results 参数

echo "自动仿真流程已完成。"
deactivate # 注销虚拟环境 