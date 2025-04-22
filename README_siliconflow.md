# 通过siliconflow.cn使用DeepSeek API的指南

## 简介

本文档介绍如何将自动仿真系统升级为使用siliconflow.cn平台提供的DeepSeek API。通过这种方式，您可以使用OpenAI兼容的API接口访问DeepSeek系列大型语言模型，用于生成TCAD仿真的参数优化建议和分析结果。

## 准备工作

### 1. 安装OpenAI Python库

```bash
pip install --upgrade openai
```

### 2. 获取API密钥

请访问[siliconflow.cn](https://www.siliconflow.cn)注册账号并获取API密钥。获取的API密钥格式应类似于：

```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 使用方法

### 1. 直接测试API

您可以使用提供的测试脚本`test_deepseek_siliconflow.py`来测试API连接：

```bash
cd /home/tcad/STDB/MyProjects/AI_Lab/MCT-SEE-Normal-Old
python3 auto_sim/test_deepseek_siliconflow.py
```

在运行测试脚本前，请确保将API密钥替换为您从siliconflow.cn获取的真实密钥。

### 2. 更新现有DeepSeekInteraction类

如果您希望更新现有系统以使用siliconflow API，可以使用`update_deepseek_api.py`脚本：

```bash
cd /home/tcad/STDB/MyProjects/AI_Lab/MCT-SEE-Normal-Old
python3 auto_sim/update_deepseek_api.py
```

该脚本会自动备份原始文件并更新`deepseek_interaction.py`以支持siliconflow API。

### 3. 在配置文件中启用siliconflow API

更新配置文件`auto_sim_config.json`，添加以下参数：

```json
{
  "api_key": "YOUR_API_KEY_FROM_CLOUD_SILICONFLOW_CN",
  "use_siliconflow": true,
  ...其他配置参数...
}
```

## API调用示例

### 基本调用示例

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY_FROM_CLOUD_SILICONFLOW_CN",
    base_url="https://api.siliconflow.cn/v1"
)

response = client.chat.completions.create(
    model='Pro/deepseek-ai/DeepSeek-R1',
    messages=[
        {'role': 'system', 'content': "你是一位半导体器件物理和辐射效应专家。"},
        {'role': 'user', 'content': "请分析单粒子效应对MOS器件性能的影响。"}
    ],
    temperature=0.7,
    max_tokens=2000
)

# 获取响应内容
content = response.choices[0].message.content
print(content)
```

### 流式响应示例

对于长回答，使用流式响应可以更快获得部分结果：

```python
response = client.chat.completions.create(
    model='Pro/deepseek-ai/DeepSeek-R1',
    messages=[
        {'role': 'system', 'content': "你是一位半导体器件物理和辐射效应专家。"},
        {'role': 'user', 'content': "请详细分析单粒子效应对MOS器件性能的影响。"}
    ],
    stream=True
)

for chunk in response:
    if not chunk.choices:
        continue
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
        print(chunk.choices[0].delta.reasoning_content, end="", flush=True)
```

## 与自动仿真系统的集成

新的`deepseek_api.py`模块已经完全支持通过siliconflow.cn调用DeepSeek API。集成到自动仿真系统中的用法示例：

```python
from auto_sim.deepseek_api import DeepSeekAPI

# 初始化API，设置use_simulation=False使用真实API调用
api = DeepSeekAPI(
    project_path="/path/to/project",
    api_key="YOUR_API_KEY_FROM_CLOUD_SILICONFLOW_CN",
    use_simulation=False
)

# 获取参数优化建议
suggestions = api.get_optimization_suggestions(
    iteration=1,
    params=current_params,
    simulation_results=sim_results
)

# 使用建议的参数进行下一轮仿真
print(f"优化建议: {suggestions}")
```

## 故障排除

如果遇到API调用失败，请检查：

1. API密钥是否正确
2. 网络连接是否正常
3. 请求格式是否符合要求

对于API调用失败，系统会自动回退到模拟模式，确保仿真流程不会中断。

## 支持的模型

当前支持的模型包括：

- `Pro/deepseek-ai/DeepSeek-R1` - 推荐用于仿真参数优化
- 其他可能可用的模型，请参考siliconflow.cn文档

## 更多信息

有关siliconflow平台和DeepSeek模型的更多信息，请访问[siliconflow.cn](https://www.siliconflow.cn)官网。 