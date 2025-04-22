#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from auto_sim.deepseek_interaction import DeepSeekInteraction

# 测试markdown解析功能
def test_markdown_parsing():
    print("测试markdown响应解析功能...")
    
    # 创建一个DeepSeekInteraction实例
    api_key = os.environ.get("DEEPSEEK_API_KEY", "sk-buspthftjrkhcudljfardlbubjlmpfoxehgstdipajrxpccc")
    interaction = DeepSeekInteraction(api_key=api_key, simulation_mode=True)
    
    # 模拟的markdown响应
    markdown_response = """## 参数优化建议

基于当前的模拟结果，我提出以下参数调整建议：

### 建议参数

| 参数 | 建议值 |
|------|-------|
| Wtot | 45.5 |
| Wg | 10.2 |
| Tdrift | 300.0 |
| Tox | 0.1 |
| Tpoly | 0.5 |
| Tcathode | 1.0 |
| Tanode | 1.0 |
| Nsubtop | 1.0e+15 |
| Nsubbot | 1.0e+19 |
| Ndrift | 1.0e+14 |
| Npbase | 5.0e+16 |
| Nbody | 1.0e+17 |

### 优化理由

1. 调整了Wtot和Wg参数以优化器件几何结构，这有助于提高latch电压。
2. 微调了Tdrift以在维持高latch电压的同时降低能量消耗。
3. 调整了掺杂浓度参数以优化电荷分布，减少能量消耗。

这些调整应该能够保持高latch电压（>500V）的同时降低能量消耗，并将电荷收集保持在合理范围内。
"""

    # 解析markdown响应
    parsed_params = interaction._parse_markdown_response(markdown_response)
    
    # 打印解析结果
    print("\n解析结果:")
    for key, value in parsed_params.items():
        print(f"{key}: {value} ({type(value).__name__})")
    
    # 验证解析结果
    expected_keys = ["Wtot", "Wg", "Tdrift", "Tox", "Tpoly", "Tcathode", "Tanode", 
                     "Nsubtop", "Nsubbot", "Ndrift", "Npbase", "Nbody"]
    
    # 检查是否所有预期的键都存在
    missing_keys = [key for key in expected_keys if key not in parsed_params]
    if missing_keys:
        print(f"\n警告：缺少以下键: {missing_keys}")
    else:
        print("\n所有预期的参数都已正确解析。")
    
    # 检查值的类型是否正确
    for key, value in parsed_params.items():
        if not isinstance(value, (int, float)):
            print(f"警告：参数 {key} 的值不是数值类型，而是 {type(value).__name__}")

if __name__ == "__main__":
    test_markdown_parsing() 