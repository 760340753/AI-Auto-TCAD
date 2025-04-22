#!/usr/bin/env bash
# 清除项目中的冗余文件（一次性清理）
# 删除 Python 缓存
find . -type d -name '__pycache__' -exec rm -rf {} +
find . -type f -name '*.pyc' -delete
# 删除日志文件
find . -type f -name '*.log' -delete
rm -f cmlog.txt SVisualTcl.log
# 可根据需要删除其他临时/缓存文件

echo "冗余文件已清理完毕，检查上述输出确保没有误删。" 