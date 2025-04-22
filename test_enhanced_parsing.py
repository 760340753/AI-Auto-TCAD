#!/usr/bin/env python3

import sys
import json
import logging
sys.path.append('/home/tcad/STDB/MyProjects/AI_Lab/MCT-SEE-Normal-Old')
from auto_sim.deepseek_interaction import DeepSeekInteraction

# 设置日志级别
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_enhanced_parsing():
    """测试增强的Markdown解析功能"""
    
    # 创建DeepSeekInteraction实例
    deepseek = DeepSeekInteraction(api_key="test-key", simulate=True)
    
    # 测试例1: 英文描述格式
    test_string1 = """
# TCAD Simulation Analysis

Based on the current simulation results, I recommend the following parameter adjustments:

Wtot should be adjusted to 47.5
For Wg, recommend 8.5
Tdrift needs to be 335
Tox should be set to 0.075
Increase Tpoly to 0.6
Decrease Tcathode to 0.85
Set Doping1 to 1.3e17
Adjust Doping2 to 5.7e15

Please use these parameters for the next simulation round.
"""

    # 测试例2: JSON格式嵌入
    test_string2 = """
# TCAD Simulation Analysis

I've analyzed the simulation results and calculated the optimal parameters.

```json
{
  "parameters": {
    "Wtot": 49.75,
    "Wg": 9.25,
    "Tdrift": 325.0,
    "Tox": 0.08,
    "Tpoly": 0.5,
    "Tcathode": 0.9,
    "Doping1": 1.2e17,
    "Doping2": 5.6e15,
    "Doping3": 1.05e13
  }
}
```

These parameters should improve the performance of your device.
"""

    # 测试例3: 直接JSON格式
    test_string3 = """
# TCAD Simulation Analysis

Based on the simulation results, here are my recommended parameters:

```json
{
  "Wtot": 51.25,
  "Wg": 8.75,
  "Tdrift": 330.5,
  "Tox": 0.085,
  "Tpoly": 0.55,
  "Tcathode": 1.0,
  "Doping1": 1.35e17,
  "Doping2": 5.5e15,
  "Doping3": 1.1e13
}
```

Please use these values for your next simulation iteration.
"""

    # 测试例4: 混合格式带单位
    test_string4 = """
# TCAD Simulation Analysis

For the next iteration, I propose the following parameters:

| Parameter | Value |
|-----------|-------|
| Wtot | 52.0 um |
| Wg | 9.5 um |
| Tdrift | 328.0 um |

Additionally:
- Tox should be 0.082 um
- Tpoly is recommended to be 0.51 um
- For Tcathode, use 0.92 um
- Set Doping1 to 1.28e17 cm^-3
- Doping2 proposed value: 5.65e15 cm^-3

These parameters should optimize your device performance.
"""

    # 测试例5: 非标准输入（空字符串）
    test_string5 = ""

    # 测试例6: 非标准输入（非字符串对象）
    test_string6 = None

    # 执行测试
    print("\n=== 测试例1: 英文描述格式 ===")
    result1 = deepseek._parse_markdown_response(test_string1)
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    print("\n=== 测试例2: JSON格式嵌入 ===")
    result2 = deepseek._parse_markdown_response(test_string2)
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    print("\n=== 测试例3: 直接JSON格式 ===")
    result3 = deepseek._parse_markdown_response(test_string3)
    print(json.dumps(result3, indent=2, ensure_ascii=False))
    
    print("\n=== 测试例4: 混合格式带单位 ===")
    result4 = deepseek._parse_markdown_response(test_string4)
    print(json.dumps(result4, indent=2, ensure_ascii=False))
    
    print("\n=== 测试例5: 非标准输入（空字符串） ===")
    result5 = deepseek._parse_markdown_response(test_string5)
    print(json.dumps(result5, indent=2, ensure_ascii=False))
    
    print("\n=== 测试例6: 非标准输入（非字符串对象） ===")
    result6 = deepseek._parse_markdown_response(test_string6)
    print(json.dumps(result6, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_enhanced_parsing() 