#!/usr/bin/env python3

import sys
import json
import logging
sys.path.append('/home/tcad/STDB/MyProjects/AI_Lab/MCT-SEE-Normal-Old')
from auto_sim.deepseek_interaction import DeepSeekInteraction

# 设置日志级别
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_all_formats():
    """综合测试所有格式的Markdown解析功能"""
    
    # 创建DeepSeekInteraction实例
    deepseek = DeepSeekInteraction(api_key="test-key", simulate=True)
    
    # 综合测试字符串，包含所有支持的格式
    test_string = """
# TCAD模拟分析综合报告

## 参数分析与建议

我已分析了当前参数配置，发现以下几点需要优化:

### 表格形式建议

| 参数 | 当前值 | 建议值 | 单位 |
|------|--------|--------|------|
| Wtot | 45.5 | 52.75 | um |
| Wg | 8.5 | 9.25 | um |
| Tdrift | 320 | 335.5 | um |

### 文本形式建议

Tox应该调整为0.078 um
对于Tpoly，建议值是0.53 um
增加Tcathode到0.94 um
把Doping1设为1.3e17 cm^-3
Doping2需要增加到5.45e15 cm^-3
Doping3应该设为1.05e13 cm^-3

### 英文描述建议

Wn should be set to 0.85 um
Increase Ln to 0.5 um
For Csub, recommend 1.0e-12
The best value for Rsub is 100

### JSON格式参数

```json
{
  "additional_params": {
    "Ldrift": 4.5,
    "Doping4": 1.0e16,
    "Tmetal": 0.65
  }
}
```

### 特殊格式和边界条件

最佳Cplug值是5.0e-13
Rplug的值需要精确控制在7.5
目前可以尝试设置Hmetal = 0.75
但如果工艺允许，可以将Hmetal调整到0.8

## 预期结果

以上参数调整应该能够使阳极电压提高15%，同时降低能量消耗约8%。
"""

    # 执行测试
    print("\n=== 综合测试 ===")
    result = deepseek._parse_markdown_response(test_string)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 验证是否提取了所有预期参数
    expected_params = {
        "Wtot", "Wg", "Tdrift", "Tox", "Tpoly", "Tcathode", 
        "Doping1", "Doping2", "Doping3", "Wn", "Ln", "Csub", "Rsub",
        "Ldrift", "Doping4", "Tmetal", "Cplug", "Rplug", "Hmetal"
    }
    
    actual_params = set(result.keys())
    missing_params = expected_params - actual_params
    unexpected_params = actual_params - expected_params
    
    print("\n=== 验证结果 ===")
    print(f"预期参数数量: {len(expected_params)}")
    print(f"实际提取参数数量: {len(actual_params)}")
    print(f"缺失参数: {missing_params if missing_params else '无'}")
    print(f"意外参数: {unexpected_params if unexpected_params else '无'}")
    print(f"解析成功率: {len(actual_params.intersection(expected_params))/len(expected_params)*100:.2f}%")

if __name__ == "__main__":
    test_all_formats() 