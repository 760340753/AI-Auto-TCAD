#!/bin/bash

echo "=== 开始重新构建Python 3.11.4 ==="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
  echo "错误: 请以root用户运行此脚本"
  exit 1
fi

# 安装依赖
echo "安装依赖包..."
yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel

# 进入Python源代码目录
cd /home/tcad/Python-3.11.4
if [ $? -ne 0 ]; then
  echo "错误: 无法切换到Python源代码目录"
  exit 1
fi

# 清理之前的编译
echo "清理之前的编译..."
make clean

# 配置
echo "配置Python编译选项..."
./configure --enable-optimizations --with-openssl
if [ $? -ne 0 ]; then
  echo "错误: Python配置失败"
  exit 1
fi

# 编译
echo "编译Python..."
make -j 2
if [ $? -ne 0 ]; then
  echo "错误: Python编译失败"
  exit 1
fi

# 安装
echo "安装Python..."
make altinstall
if [ $? -ne 0 ]; then
  echo "错误: Python安装失败"
  exit 1
fi

# 验证安装
echo "验证安装..."
/usr/local/bin/python3.11 -c "import ssl; print('SSL支持已启用')"
if [ $? -ne 0 ]; then
  echo "错误: SSL模块验证失败"
  exit 1
fi

echo "Python 3.11.4 安装完成，并已支持SSL"
exit 0 