# Sentaurus Workbench自动化仿真系统

本项目实现了基于Python和SWB API的自动化仿真系统，可以自动添加新实验并运行仿真。

## 环境配置

1. 确保已安装Python 3.11及以上版本
2. 确保已正确配置Sentaurus环境变量（STROOT和STRELEASE）
3. 已安装SWB API需要的Python包（swbutils和swbpy2）

## 使用方法

### 方法一：使用启动脚本（推荐）

直接运行启动脚本，该脚本会自动配置环境并运行仿真：

```bash
./run_swb_auto.sh
```

### 方法二：手动运行

1. 确保已设置正确的环境变量：

```bash
source ~/sentaurus_env.sh
```

2. 激活Python虚拟环境：

```bash
source swb_env/bin/activate
```

3. 运行自动化脚本：

```bash
python3.11 swb_auto.py
```

## 配置参数

在`swb_auto.py`文件中，可以修改以下参数：

- `PROJECT_PATH`：SWB项目路径
- `AUTO_RUN`：是否自动运行仿真
- `sde_params`：器件结构参数
- `sdevice_params`：器件性能仿真参数
- 各种等待时间参数

## 工作流程

1. 检查环境变量
2. 打开SWB工程
3. 添加新实验（新参数路径）
4. 保存工程并刷新
5. 预处理和运行仿真（如启用AUTO_RUN）
6. 监控节点状态
7. 生成迭代报告

## 日志和报告

- 日志文件存储在`logs`目录下
- 迭代报告保存在项目根目录下的`iteration_report.md`中

## 故障排除

如果遇到问题，请检查：

1. Python版本是否为3.11或更高
2. Sentaurus环境变量是否正确设置
3. 查看日志文件，确认错误信息
4. 确保SWB工程路径正确 