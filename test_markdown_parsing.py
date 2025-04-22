#!/usr/bin/env python3

import sys
import json
import logging
sys.path.append('/home/tcad/STDB/MyProjects/AI_Lab/MCT-SEE-Normal-Old')
from auto_sim.deepseek_interaction import DeepSeekInteraction

# 设置日志级别
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_parse_markdown():
    """测试不同格式的markdown响应解析"""
    
    # 创建DeepSeekInteraction实例
    deepseek = DeepSeekInteraction(api_key="test-key", simulate=True)
    
    # 测试例1: 表格格式
    test_string1 = """
# TCAD模拟分析

根据提供的模拟参数和结果，我建议以下参数调整：

| 参数 | 建议值 |
|------|--------|
| Wtot | 50.5 |
| Wg | 9.75 |
| Tdrift | 327.45 |
| Tox | 0.085 |
| Tpoly | 0.52 |
| Tcathode | 0.95 |
| Doping1 | 1.25e17 |
| Doping2 | 5.5e15 |
| Doping3 | 1.1e13 |

请根据以上建议进行下一次模拟。
"""

    # 测试例2: 文本格式（键值对）
    test_string2 = """
# TCAD模拟分析

分析了当前模拟参数后，我建议以下调整：

- Wtot: 48.75
- Wg = 10.25
- Tdrift: 320.5
- Tox = 0.09
- Tpoly: 0.48
- Tcathode = 1.05

请根据上述调整进行下一轮模拟。
"""

    # 测试例3: 中文描述格式
    test_string3 = """
# TCAD模拟分析

根据当前的模拟结果，我有以下建议：

Wtot应该调整为45.5
对于Wg，建议值是8.75
Tdrift需要增加到330
Tox应该保持在0.08
Tpoly需要增加到0.55
Tcathode应该调整为1.0nm

请采用这些参数进行下一轮模拟。
"""

    # 测试例4: 混合格式
    test_string4 = """
# TCAD模拟分析

分析结果如下：

| 参数 | 建议值 |
|------|--------|
| Wtot | 52.5 |
| Wg | 9.0 |

另外，Tdrift应该调整为325.5
对于Tox，建议值是0.075
Tpoly = 0.5
Tcathode: 0.9

请使用这些参数进行进一步优化。
"""

    # 执行测试
    print("\n=== 测试例1: 表格格式 ===")
    result1 = deepseek._parse_markdown_response(test_string1)
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    print("\n=== 测试例2: 文本格式（键值对） ===")
    result2 = deepseek._parse_markdown_response(test_string2)
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    print("\n=== 测试例3: 中文描述格式 ===")
    result3 = deepseek._parse_markdown_response(test_string3)
    print(json.dumps(result3, indent=2, ensure_ascii=False))
    
    print("\n=== 测试例4: 混合格式 ===")
    result4 = deepseek._parse_markdown_response(test_string4)
    print(json.dumps(result4, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_parse_markdown() 