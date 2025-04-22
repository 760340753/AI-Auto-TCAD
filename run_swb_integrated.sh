#!/bin/bash
# Sentaurus Workbench自动化仿真系统 - 整合版启动脚本
# 此脚本配置环境并运行swb_integrated.py

# 显示脚本开始运行
echo "==============================================="
echo "启动Sentaurus Workbench自动化仿真系统 - 整合版"
echo "==============================================="

# 设置字符编码
export PYTHONIOENCODING=UTF-8
export LANG=en_US.UTF-8

# 导入Sentaurus环境
if [ -f "sentaurus_env.sh" ]; then
    echo "导入Sentaurus环境..."
    source ./sentaurus_env.sh
else
    echo "警告: 未找到sentaurus_env.sh，请确保已设置Sentaurus环境变量"
fi

# 检查Python版本
PYTHON_CMD="python3.11"
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "错误: 未找到Python 3.11"
    echo "请确保已安装Python 3.11"
    exit 1
fi

echo "使用Python: $($PYTHON_CMD --version)"

# 检查虚拟环境
if [ -d "swb_env" ]; then
    echo "激活Python虚拟环境..."
    source swb_env/bin/activate
fi

# 检查必要的Python包
echo "检查所需Python包..."
$PYTHON_CMD -c "
try:
    import swbpy2
    print('✓ swbpy2 已安装')
except ImportError:
    print('✗ 未找到swbpy2，这可能导致脚本运行失败')

try:
    import swbutils
    print('✓ swbutils 已安装')
except ImportError:
    print('✗ 未找到swbutils，这可能导致脚本运行失败')

try:
    import numpy
    print('✓ numpy 已安装')
except ImportError:
    print('✗ 未找到numpy')

try:
    import pandas
    print('✓ pandas 已安装')
except ImportError:
    print('✗ 未找到pandas')

try:
    import matplotlib
    print('✓ matplotlib 已安装')
except ImportError:
    print('✗ 未找到matplotlib')
"

# 显示环境信息
echo ""
echo "==============================================="
echo "环境信息:"
echo "==============================================="
echo "Python路径: $(which $PYTHON_CMD)"
echo "项目目录: $(pwd)"
if [ -n "$STROOT" ]; then
    echo "STROOT: $STROOT"
fi
if [ -n "$STRELEASE" ]; then
    echo "STRELEASE: $STRELEASE"
fi
echo "==============================================="

# 解析命令行参数
USE_CONFIG=""
USE_PROJECT=""
NO_RUN=""
ANALYZE=""
ANALYZE_ALL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            USE_CONFIG="--config $2"
            shift 2
            ;;
        --project)
            USE_PROJECT="--project $2"
            shift 2
            ;;
        --no-run)
            NO_RUN="--no-run"
            shift
            ;;
        --analyze)
            ANALYZE="--analyze $2"
            shift 2
            ;;
        --analyze-all)
            ANALYZE_ALL="--analyze-all"
            shift
            ;;
        *)
            echo "未知选项: $1"
            shift
            ;;
    esac
done

# 运行整合版脚本
echo ""
echo "==============================================="
echo "运行Sentaurus Workbench自动化仿真系统 - 整合版"
echo "==============================================="

$PYTHON_CMD ./swb_integrated.py $USE_CONFIG $USE_PROJECT $NO_RUN $ANALYZE $ANALYZE_ALL

# 检查运行结果
if [ $? -eq 0 ]; then
    echo "==============================================="
    echo "自动化仿真完成"
    echo "==============================================="
else
    echo "==============================================="
    echo "自动化仿真异常退出"
    echo "==============================================="
    echo "请检查日志文件: swb_integrated.log"
fi

# 如果使用了虚拟环境，退出环境
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 