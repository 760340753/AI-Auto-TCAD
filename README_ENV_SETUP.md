# 环境配置详细说明

要使用SWB自动化脚本，需要配置以下环境：

## 1. 安装Python 3.11

当前检测到SSL模块问题，需要重新编译Python以支持SSL，步骤如下：

```bash
# 以root用户执行
su - root

# 安装必要的依赖
yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel

# 进入Python源码目录
cd /home/tcad/Python-3.11.4

# 配置编译选项，确保启用SSL支持
./configure --enable-optimizations --with-openssl=/usr

# 编译安装
make -j 2
make altinstall
```

## 2. 安装Python依赖

安装numpy和其他必要的包：

```bash
# 安装pip
python3.11 -m ensurepip --upgrade

# 安装numpy（可能需要手动下载并本地安装）
python3.11 -m pip install numpy --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

## 3. 安装SWB Python API

```bash
# 切换到Sentaurus库目录
cd $STROOT_LIB

# 安装swbutils和swbpy2
python3.11 -m pip install swbutils-1.1.4-cp311-none-linux_x86_64.whl --force-reinstall
python3.11 -m pip install swbpy2-2.2.0-cp311-none-linux_x86_64.whl --force-reinstall
```

## 4. 配置环境变量

确保在`~/sentaurus_env.sh`中包含以下环境变量：

```bash
export STROOT=/usr/synopsys/sentaurus/V-2024.03
export STRELEASE=V-2024.03
export PATH=$STROOT/bin:$PATH
export LD_LIBRARY_PATH=$STROOT/tcad/$STRELEASE/linux64/lib/:$LD_LIBRARY_PATH
export STROOT_LIB=$STROOT/tcad/$STRELEASE/lib
export PATH=/usr/local/bin:$PATH
```

## 5. 为项目创建Python虚拟环境

```bash
cd /home/tcad/STDB/MyProjects/AI_Lab/MCT-SEE-Normal-Old
python3.11 -m venv swb_env

# 激活虚拟环境
source swb_env/bin/activate

# 在虚拟环境中安装必要的包
pip install numpy --trusted-host pypi.org --trusted-host files.pythonhosted.org
pip install $STROOT_LIB/swbutils-1.1.4-cp311-none-linux_x86_64.whl --force-reinstall
pip install $STROOT_LIB/swbpy2-2.2.0-cp311-none-linux_x86_64.whl --force-reinstall
```

## 6. 测试环境配置

```bash
# 测试Python版本
python3.11 --version

# 测试SWB Python API导入
python3.11 -c "from swbpy2 import *; print('SWB API 导入成功')"
```

## 疑难解答

如果遇到SSL相关错误，可以使用`--trusted-host`参数绕过SSL验证：

```bash
python3.11 -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package-name>
```

如果依然无法解决SSL问题，可以手动下载所需的whl文件到本地安装。
