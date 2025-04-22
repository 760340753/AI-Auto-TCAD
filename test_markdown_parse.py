#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from pathlib import Path

# 添加auto_sim到Python路径
sys.path.append(os.path.abspath("."))
from auto_sim.deepseek_interaction import DeepSeekInteraction

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

# 测试具有中文表头的markdown
def test_chinese_markdown_parsing():
    """测试包含中文表头的Markdown响应解析功能"""
    print("\n开始测试中文表头Markdown响应解析...")
    
    # 创建一个用于测试的带中文表头的markdown响应
    markdown_response = """## 参数优化建议

基于当前的模拟结果，我提出以下参数调整建议：

### 建议参数

| 参数 | 建议值 |
|------|-------|
| Wtot | 48.75 |
| Wg | 9.8 |
| Tdrift | 295.5 |
| Tox | 0.105 |
| Tpoly | 0.48 |
| Tcathode | 0.95 |
| Tanode | 1.02 |
| Nsubtop | 1.2e+15 |
| Nsubbot | 1.05e+19 |
| Ndrift | 1.1e+14 |
| Npbase | 4.8e+16 |
| Nbody | 9.5e+16 |

### 优化理由

1. 略微减小Wtot和Wg来降低能量消耗
2. 优化Tdrift以在保持latch电压的同时减少能量消耗
3. 调整了掺杂浓度以优化电荷分布
4. 精细调整了几何尺寸以保持整体性能平衡

这些参数应该能够在保持高latch电压的同时降低能量消耗。
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
    
    print("\n中文表头Markdown解析测试完成")

if __name__ == "__main__":
    test_markdown_parsing()
    test_chinese_markdown_parsing() 