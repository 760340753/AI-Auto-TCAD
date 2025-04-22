#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import logging
import json
from auto_sim.deepseek_interaction import DeepSeekInteraction

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_improved_parsing")

def test_improved_parsing():
    print("开始测试改进的Markdown解析功能...")
    
    # 创建DeepSeekInteraction实例 - 修正初始化参数
    deepseek = DeepSeekInteraction(api_key="test_key", simulation_mode=True)
    
    # 测试字符串1：包含参数表格和建议
    test_string_1 = """
分析完成后，我对TCAD模型参数提出以下优化建议：

| 参数 | 建议值 |
|------|--------|
| Wtot | 50.7 |
| Wg | 9.53 |
| Tdrift | 327.57 |
| Tox | 0.021 |
| Tpoly | 0.4 |
| Tcathode | 1.1 |
| Ndrift | 2.1e15 |
| Lch | 5.2 |
| Lgc | 4.1 |
| Nsub | 8.3e16 |

这些参数调整应该能够帮助改善器件的性能和抗辐照能力。
"""

    # 测试字符串2：混合格式的参数描述
    test_string_2 = """
基于当前的仿真结果，我建议以下参数调整：

**Wtot**: 应调整为 52.5 μm
**Wg**: 建议值为 10.1 μm
**Tdrift**: 建议调整到 325 μm
Tox 应当保持在 0.02 μm左右
Tpoly = 0.45 μm
Tcathode 值调整为 1.05 μm
Ndrift: 2.5e15 cm^-3
Lch值: 5.3 μm
对于Lgc，建议使用4.2μm
Nsub建议值： 8.5e16 cm^-3
"""

    # 期望的参数字典1
    expected_params_1 = {
        "wtot": 50.7,
        "wg": 9.53,
        "tdrift": 327.57,
        "tox": 0.021,
        "tpoly": 0.4,
        "tcathode": 1.1,
        "ndrift": 2.1e15,
        "lch": 5.2,
        "lgc": 4.1,
        "nsub": 8.3e16
    }
    
    # 期望的参数字典2
    expected_params_2 = {
        "wtot": 52.5,
        "wg": 10.1,
        "tdrift": 325.0,
        "tox": 0.02,
        "tpoly": 0.45,
        "tcathode": 1.05,
        "ndrift": 2.5e15,
        "lch": 5.3,
        "lgc": 4.2,
        "nsub": 8.5e16
    }
    
    # 测试解析第一个字符串
    print("\n--- 测试字符串1 (表格格式) ---")
    params_1 = deepseek._parse_markdown_response(test_string_1)
    print(f"解析结果: {json.dumps(params_1, indent=2, ensure_ascii=False)}")
    
    # 测试解析第二个字符串
    print("\n--- 测试字符串2 (混合格式) ---")
    params_2 = deepseek._parse_markdown_response(test_string_2)
    print(f"解析结果: {json.dumps(params_2, indent=2, ensure_ascii=False)}")
    
    # 评估结果1
    print("\n--- 评估结果1 ---")
    success_count_1 = 0
    missing_params_1 = []
    extra_params_1 = []
    
    for param, value in expected_params_1.items():
        if param in params_1:
            if abs(params_1[param] - value) < 0.001:
                success_count_1 += 1
            else:
                print(f"参数值不匹配: {param} 期望值 {value}, 得到值 {params_1[param]}")
        else:
            missing_params_1.append(param)
    
    for param in params_1:
        if param not in expected_params_1:
            extra_params_1.append(param)
    
    print(f"找到的参数: {success_count_1}/{len(expected_params_1)}")
    print(f"缺失的参数: {missing_params_1}")
    print(f"额外的参数: {extra_params_1}")
    
    # 评估结果2
    print("\n--- 评估结果2 ---")
    success_count_2 = 0
    missing_params_2 = []
    extra_params_2 = []
    
    for param, value in expected_params_2.items():
        if param in params_2:
            if abs(params_2[param] - value) < 0.001:
                success_count_2 += 1
            else:
                print(f"参数值不匹配: {param} 期望值 {value}, 得到值 {params_2[param]}")
        else:
            missing_params_2.append(param)
    
    for param in params_2:
        if param not in expected_params_2:
            extra_params_2.append(param)
    
    print(f"找到的参数: {success_count_2}/{len(expected_params_2)}")
    print(f"缺失的参数: {missing_params_2}")
    print(f"额外的参数: {extra_params_2}")
    
    # 计算总体成功率
    total_success = success_count_1 + success_count_2
    total_params = len(expected_params_1) + len(expected_params_2)
    success_rate = (total_success / total_params) * 100
    
    print(f"\n总体成功率: {success_rate:.2f}%")
    
    # 最终评估
    if success_count_1 == len(expected_params_1) and success_count_2 == len(expected_params_2):
        print("\n✅ 所有参数均被正确解析!")
    else:
        print("\n❌ 存在部分参数未被正确解析")

if __name__ == "__main__":
    test_improved_parsing()
    print("\n测试完成！") 