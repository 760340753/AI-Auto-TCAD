# Sentaurus Workbench自动化仿真系统 - 整合版用户指南

## 简介

Sentaurus Workbench自动化仿真系统整合版结合了简单版本`mct_auto_sim.py`的稳定性和高级模块化版本`auto_sim/`的强大功能，为用户提供了一个更加灵活、强大且易于使用的自动化仿真工具。

本系统能够自动添加新实验、运行仿真、分析结果，并生成报告，大大提高了Sentaurus Workbench的工作效率。

## 系统特点

- **自动模式检测**：能够自动检测可用模块，在高级模块不可用时回退到基本功能
- **兼容性设计**：与原有的`mct_auto_sim.py`参数格式兼容
- **结果分析能力**：支持IV特性和SEE结果的提取和分析
- **报告生成**：自动生成仿真迭代报告
- **灵活配置**：支持通过配置文件、命令行参数或默认值配置系统

## 快速入门

### 基本用法

直接使用启动脚本运行系统：

```bash
./run_swb_integrated.sh
```

这将使用默认配置运行自动化仿真系统，添加新实验并运行仿真。

### 命令行选项

启动脚本支持以下命令行选项：

```bash
./run_swb_integrated.sh [选项]

选项:
  --config FILE    指定配置文件路径
  --project DIR    指定项目目录路径
  --no-run         仅添加实验，不自动运行仿真
  --analyze ID     分析指定节点ID的结果
  --analyze-all    分析所有叶节点的结果
```

例如，要使用自定义配置文件并运行仿真：

```bash
./run_swb_integrated.sh --config my_config.json
```

要仅添加实验但不运行仿真：

```bash
./run_swb_integrated.sh --no-run
```

要分析特定节点的结果：

```bash
./run_swb_integrated.sh --analyze 123
```

### 配置文件格式

配置文件使用JSON格式，示例如下：

```json
{
  "PROJECT_PATH": "/path/to/your/project",
  "AUTO_RUN": true,
  "REPORT_PATH": "iteration_report.md",
  "sde_params": {
    "Wtot": 50,
    "Wg": 10,
    "Wcp": 15,
    "Wcs": 4,
    "Tdrift": 320,
    "TPc": 0.2,
    "TNb": 1.5,
    "TNa": 1.5,
    "TPb": 5,
    "TPa": 0.6,
    "Tox": -0.2,
    "Tpoly": -2,
    "Tcathode": -4,
    "Zeropoint": 0,
    "Pc": 1e19,
    "Nb": 1.2e18,
    "Na": 1e15,
    "Ndrift": 5e13,
    "Npoly": 1e21,
    "Pb": 1e17,
    "Pa": 5e16,
    "x": 8.6,
    "Length": 35
  },
  "sdevice_params": ["-", 90, 800]
}
```

## 系统详解

### 工作流程

1. **环境检查**：验证Python版本和必要模块
2. **配置加载**：从命令行参数或配置文件加载配置
3. **项目打开**：打开SWB工程
4. **添加实验**：添加新的实验节点
5. **仿真运行**：如果启用AUTO_RUN，预处理并运行新节点
6. **状态监控**：监控节点运行状态
7. **结果分析**：如果请求，分析仿真结果
8. **报告生成**：生成迭代报告

### 模块结构

整合版本由以下主要部分组成：

- **主脚本**：`swb_integrated.py`
- **启动脚本**：`run_swb_integrated.sh`
- **高级模块**：
  - `auto_sim/parameter_manager.py`：参数管理
  - `auto_sim/swb_interaction.py`：SWB交互
  - `auto_sim/result_analyzer.py`：结果分析

### 日志和报告

系统生成两种主要的输出文件：

1. **日志文件**：`swb_integrated.log`，包含详细的运行日志
2. **迭代报告**：默认为`iteration_report.md`，包含每次迭代的参数和运行状态

## 高级功能

### 结果分析

可以使用`--analyze`或`--analyze-all`选项分析仿真结果：

```bash
./run_swb_integrated.sh --analyze 123
```

分析结果将以JSON格式输出，包含IV特性和SEE结果等信息。

### 自定义参数

通过修改配置文件，可以自定义各种参数：

```json
{
  "sde_params": {
    "Wtot": 60,
    "Wg": 15,
    ...
  }
}
```

## 故障排除

### 常见问题

1. **模块导入错误**:
   ```
   错误: swbpy2模块未找到，请确保已正确安装
   ```
   解决: 确保已安装必要的Python包，可以使用pip安装:
   ```bash
   pip install swbutils swbpy2
   ```

2. **项目路径错误**:
   ```
   错误: 项目路径不存在
   ```
   解决: 检查配置中的项目路径是否正确，确保路径存在。

3. **无法检测到新节点**:
   ```
   警告: 添加实验后未检测到新的叶节点
   ```
   解决: 检查参数配置，确保参数与现有实验有差异。可能需要先删除一些现有实验。

### 日志查看

系统会生成详细的日志文件`swb_integrated.log`，可以通过查看日志文件来诊断问题：

```bash
cat swb_integrated.log
```

或者使用tail命令实时查看日志：

```bash
tail -f swb_integrated.log
```

## 高级定制

对于有编程经验的用户，可以通过以下方式进一步定制系统：

### 添加新分析功能

1. 修改`auto_sim/result_analyzer.py`，添加新的分析方法
2. 在`swb_integrated.py`中的`analyze_results`方法中调用新添加的分析方法

### 集成外部优化算法

1. 创建新的参数优化模块
2. 在`swb_integrated.py`中添加对新模块的调用
3. 使用优化算法生成的参数更新`sde_params`和`sdevice_params`

## 结语

Sentaurus Workbench自动化仿真系统整合版结合了简单版本的稳定性和高级模块化版本的强大功能，为用户提供了一个强大而灵活的自动化工具。通过本用户指南，您应该能够顺利使用系统的各项功能，提高工作效率。

如有任何问题或建议，请联系项目维护人员。 