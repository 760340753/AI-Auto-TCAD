# AI-Auto-TCAD

基于 DeepSeek AI 与 swbpy2 的通用 Sentaurus Workbench 自动化仿真与参数优化工具。使用 AI 技术指导半导体器件设计参数优化，支持 SDE+SDevice 仿真流程。

## 系统要求

- **操作系统**：Linux (CentOS 7.9)
- **Python版本**：Python 3.11
- **Sentaurus版本**：Sentaurus 2024.03
- **必要环境**：Sentaurus Workbench 必须已经启动

## 快速安装

1. 克隆仓库
   ```bash
   git clone https://github.com/760340753/AI-Auto-TCAD.git
   cd AI-Auto-TCAD
   ```

2. 在工程目录下运行安装命令
   ```bash
   python3.11 -m pip install -e .
   ```

3. 或使用自动安装命令（会自动创建虚拟环境）
   ```bash
   python3.11 -m fs_auto_sim.cli install
   ```

4. 激活虚拟环境
   ```bash
   source .fs_auto_sim_env/bin/activate
   ```

## 使用方法

### 启动图形界面

确保已激活虚拟环境，然后运行:

```bash
fs-sim-ui
```

或者:

```bash
python -m fs_auto_sim.cli ui
```

### 启动命令行界面（无需图形环境）

如果您的环境没有图形界面支持，可以使用命令行版UI:

```bash
fs-sim-console
```

或者:

```bash
python -m fs_auto_sim.cli console
```

命令行界面提供与图形界面同样的功能，包括:

- 选择工程目录
- 输入API Key
- 描述优化目标
- 查看和修改初始参数
- 检查参数唯一性
- 启动全自动仿真流程

### 界面操作指南

1. **选择工程目录**：选择包含 SWB 项目的文件夹
2. **填写 API Key**：输入 DeepSeek API Key（可选，仿真模式可留空）
3. **描述优化目标**：描述需要实现的性能指标（如"提高击穿电压同时保持导通电阻"）
4. **加载初始参数**：点击按钮加载项目初始参数
5. **检查参数唯一性**：点击按钮检查初始参数是否与已有实验重复
6. **开始全自动仿真**：点击启动自动化仿真与参数优化流程
7. **查看报告**：查看迭代过程报告与最终优化结果

## 注意事项

- 本工具当前仅支持 Sentaurus 2024.03 版本，不保证兼容其他版本
- 使用前请确保 Sentaurus Workbench 已启动并加载了目标工程
- 工程必须包含 SDE (*.dvs.cmd) + SDevice (*.des.cmd) 模块
- 启动前确保工程目录下存在初始参数文件 Parameter/Initial_Parameter/initial_params.json

## 问题反馈

如有问题或建议，请提交 Issue 或联系: 760340753@qq.com
