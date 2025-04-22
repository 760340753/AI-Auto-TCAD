# Sentaurus Workbench 自动化仿真系统安装指南

本文档提供了如何安装和设置 Sentaurus Workbench 自动化仿真系统的指南。

## 安装要求

- CentOS/RHEL 7 或更高版本
- Python 3.11 (必须预先安装)
- Sentaurus TCAD 2024.03
- 管理员权限（用于安装依赖）

## 安装步骤

### 1. 准备工作

确保您已经安装了 Python 3.11。您可以使用以下命令检查 Python 版本：

```bash
python3.11 --version
```

如果未安装，请首先安装 Python 3.11。

### 2. 运行安装脚本

执行以下命令运行安装脚本：

```bash
chmod +x install_environment.sh
./install_environment.sh
```

安装脚本将执行以下操作：

1. 安装必要的系统依赖
2. 在 `~/sentaurus_auto` 目录下创建项目结构
3. 设置 Python 虚拟环境
4. 安装所有必要的 Python 依赖
5. 创建一个便捷的启动脚本

安装过程中的所有输出都会记录到 `install.log` 文件中。

### 3. 验证安装

安装完成后，您可以使用以下命令运行自动化仿真系统：

```bash
cd ~/sentaurus_auto
./run_swb_auto.sh
```

这将启动自动化仿真流程。

## 目录结构

安装完成后，将创建以下目录结构：

```
~/sentaurus_auto/
├── MCT-SEE-Normal-Old/        # 仿真项目目录
│   ├── auto_sim/              # 自动化仿真脚本
│   ├── Parameter/             # 参数文件
│   ├── Results/               # 仿真结果
│   ├── Reports/               # 报告
│   └── ...
├── swb_env/                   # Python 虚拟环境
└── run_swb_auto.sh            # 启动脚本
```

## 使用注意事项

- 确保您的 Sentaurus TCAD 环境已正确设置，特别是 `sentaurus_env.sh` 文件的位置
- 在修改参数后运行自动化仿真前，请备份您的数据
- 如果您的终端显示中文时出现乱码，请确保您的终端支持 UTF-8 编码

## 故障排除

如果遇到安装或运行问题，请检查 `install.log` 文件中的详细信息。常见问题包括：

1. **Python 依赖安装失败**：确保您的网络连接正常，并再次运行安装脚本
2. **启动脚本执行失败**：检查 Sentaurus 环境设置
3. **字符编码问题**：确保您的终端支持 UTF-8 编码

## 联系信息

如有任何问题或需要支持，请联系系统管理员或原始开发者。 