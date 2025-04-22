#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from pathlib import Path

# 添加auto_sim到Python路径
sys.path.append(os.path.abspath("."))
from auto_sim.deepseek_interaction import DeepSeekInteraction

# 设置API密钥
API_KEY = "sk-buspthftjrkhcudljfardlbubjlmpfoxehgstdipajrxpccc"  # 请替换为您的实际API密钥

def main():
    print("===== 测试专业版 DeepSeek-R1 模型和 Markdown 格式响应 =====")
    
    # 创建DeepSeekInteraction实例，但不启用模拟模式
    deepseek = DeepSeekInteraction(api_key=API_KEY, simulation_mode=False)
    
    # 测试参数
    test_params = {
        "Wtot": 50.0,
        "Wg": 10.0,
        "Tdrift": 300.0,
        "Tox": 0.1,
        "Tpoly": 0.5,
        "Tcathode": 1.0,
        "Tanode": 1.0,
        "Nsubtop": 1e15,
        "Nsubbot": 1e19,
        "Ndrift": 1e14,
        "Npbase": 5e16,
        "Nbody": 1e17
    }
    
    # 测试结果
    test_results = {
        "node_id": 53,
        "latchup": True,
        "latch_voltage": 780,
        "peak_current": 0.015,
        "charge_collection": 1.2e-12,
        "energy_consumption": 3.5e-9
    }
    
    # 测试专业版模型
    print("\n=== 测试1: 使用专业版 DeepSeek-R1 模型 ===")
    
    # 构建系统提示
    system_prompt = """你是一个专业的半导体器件TCAD模拟优化专家。你的任务是分析当前的TCAD模拟参数和结果，然后提供下一次迭代的优化参数建议。

请注意以下几点：
1. 你需要理解每个参数的物理含义和它们对器件性能的影响。
2. 你的目标是优化器件参数，使其满足性能目标。
3. 每次迭代时，你应该基于之前的模拟结果，提出合理的参数调整建议。
4. 所有参数调整都应该在物理可行的范围内。
5. 你的输出必须是具体的参数值，不要提供范围或描述性的建议。

请输出一个包含所有必需参数的建议，每个参数必须有确定的数值，用于下一次模拟迭代。
请以Markdown格式输出，包含参数建议表格。"""

    # 构建用户查询
    user_query = """# 迭代信息
当前迭代: 1

## 当前参数
- Wtot: 50.0
- Wg: 10.0
- Tdrift: 300.0
- Tox: 0.1
- Tpoly: 0.5
- Tcathode: 1.0
- Tanode: 1.0
- Nsubtop: 1.0e+15
- Nsubbot: 1.0e+19
- Ndrift: 1.0e+14
- Npbase: 5.0e+16
- Nbody: 1.0e+17

## 模拟结果
- node_id: 53
- latchup: True
- latch_voltage: 780
- peak_current: 0.015
- charge_collection: 1.2e-12
- energy_consumption: 3.5e-9

## 性能目标
- 使latch电压尽可能高（目标>500V）
- 降低能量消耗（energy_consumption）
- 保持电荷收集（charge_collection）在合理范围内

## 参数约束
所有参数必须在物理合理的范围内。

## 请提供优化建议
请分析上述参数和结果，提供下一次迭代的参数优化建议。你的回答必须包含以下参数的具体数值（不要给出范围）：

| 参数 | 建议值 |
|------|-------|
| Wtot | ? |
| Wg | ? |
| Tdrift | ? |
| Tox | ? |
| Tpoly | ? |
| Tcathode | ? |
| Tanode | ? |
| Nsubtop | ? |
| Nsubbot | ? |
| Ndrift | ? |
| Npbase | ? |
| Nbody | ? |
"""

    # 准备消息
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    
    print(f"使用API密钥: {API_KEY[:5]}...{API_KEY[-5:]}")
    print(f"模型: {deepseek.pro_model}")
    print("发送请求...")
    
    # 调用API
    try:
        response = deepseek._call_api(
            messages=messages,
            model_name=deepseek.pro_model,
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "text"}
        )
        
        # 获取响应内容
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        print("\n=== API响应 ===")
        print(content)
        
        print("\n=== 尝试解析Markdown响应 ===")
        parsed_params = deepseek._parse_markdown_response(content)
        print(f"解析出的参数: {json.dumps(parsed_params, indent=2)}")
        
        # 保存响应到文件
        with open("pro_model_markdown_response.md", "w") as f:
            f.write(content)
        print(f"响应已保存到 pro_model_markdown_response.md")
        
    except Exception as e:
        print(f"API调用失败: {str(e)}")
    
    # 测试常规模型JSON格式
    print("\n=== 测试2: 使用常规模型和JSON格式 ===")
    
    try:
        response = deepseek._call_api(
            messages=messages,
            model_name=deepseek.default_model,
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        # 获取响应内容
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        
        print("\n=== API响应 ===")
        print(content)
        
        # 尝试解析JSON
        if isinstance(content, str):
            try:
                json_data = json.loads(content)
                print(f"解析出的JSON: {json.dumps(json_data, indent=2)}")
            except json.JSONDecodeError:
                print("无法解析为JSON")
        else:
            print(f"解析出的JSON: {json.dumps(content, indent=2)}")
        
        # 保存响应到文件
        with open("standard_model_json_response.json", "w") as f:
            if isinstance(content, str):
                f.write(content)
            else:
                json.dump(content, f, indent=2)
        print(f"响应已保存到 standard_model_json_response.json")
        
    except Exception as e:
        print(f"API调用失败: {str(e)}")
    
    print("\n===== 测试完成 =====")

def test_markdown_parsing():
    """测试Markdown响应解析功能"""
    print("开始测试Markdown响应解析...")
    
    # 创建一个用于测试的markdown响应
    markdown_response = """## 参数优化建议

基于当前的模拟结果，我提出以下参数调整建议：

### 建议参数

| 参数 | 建议值 |
|------|-------|
| Wtot | 52.45 |
| Wg | 10.2 |
| Tdrift | 310.8 |
| Tox | 0.095 |
| Tpoly | 0.52 |
| Tcathode | 1.05 |
| Tanode | 0.98 |
| Nsubtop | 1.1e+15 |
| Nsubbot | 0.95e+19 |
| Ndrift | 0.9e+14 |
| Npbase | 5.2e+16 |
| Nbody | 1.1e+17 |

### 优化理由

1. 增加了Wtot和Wg以提高latch电压
2. 减小了Tdrift以降低能量消耗
3. 调整了Nsubtop和Ndrift浓度以优化电荷分布
4. 微调了其他几何参数，使整体结构更加平衡

这些调整应该能够在不牺牲latch电压的情况下降低能量消耗，同时保持电荷收集在合理范围内。
"""

    # 初始化DeepSeekInteraction实例
    api_key = "sk-dummy-key-for-testing"
    deepseek = DeepSeekInteraction(api_key=api_key, simulation_mode=True)
    
    # 解析markdown响应
    parsed_params = deepseek._parse_markdown_response(markdown_response)
    
    # 打印解析结果
    print("\n解析结果:")
    print(json.dumps(parsed_params, indent=2))
    
    # 验证解析结果
    expected_keys = ["Wtot", "Wg", "Tdrift", "Tox", "Tpoly", "Tcathode", 
                     "Tanode", "Nsubtop", "Nsubbot", "Ndrift", "Npbase", "Nbody"]
    
    missing_keys = [key for key in expected_keys if key not in parsed_params]
    if missing_keys:
        print(f"\n警告: 缺少以下参数: {', '.join(missing_keys)}")
    else:
        print("\n所有期望的参数都已解析")
    
    # 验证数据类型
    for key, value in parsed_params.items():
        if not isinstance(value, (int, float)):
            print(f"警告: 参数 {key} 的值 {value} 不是数值类型")
    
    print("\nMarkdown解析测试完成")

if __name__ == "__main__":
    main()
    test_markdown_parsing() 