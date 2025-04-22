#!/usr/bin/env python3

import sys
import json
import logging
sys.path.append('/home/tcad/STDB/MyProjects/AI_Lab/MCT-SEE-Normal-Old')
from auto_sim.deepseek_interaction import DeepSeekInteraction

# 设置日志级别
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_comprehensive_parsing():
    """综合测试Markdown解析功能，使用更复杂的响应格式"""
    
    # 创建DeepSeekInteraction实例
    deepseek = DeepSeekInteraction(api_key="test-key", simulate=True)
    
    # 测试例1: 复杂混合格式（含有多种表示方式和单位）
    test_string1 = """
# TCAD模拟分析报告

## 参数分析

根据迭代3的结果，我认为当前模拟存在以下问题：
1. 阳极电压不够高，需要增加耐压能力
2. 能量消耗偏高，需要优化结构减少消耗
3. 电荷收集效率可以进一步提高

## 优化建议

综合考虑物理特性和工艺限制，建议如下调整：

| 参数 | 当前值 | 建议值 | 单位 |
|------|--------|--------|------|
| Wtot | 45.5 | 52.75 | um |
| Wg | 8.5 | 9.25 | um |
| Tdrift | 320 | 335.5 | um |

此外，以下参数也需要调整：

- Tox应该减少到0.078 um
- Tpoly需要增加到0.53 um
- Tcathode应该设置为0.94 um

对于掺杂参数：
对于Doping1，建议值是1.3e17 cm^-3
将Doping2调整到5.45e15 cm^-3
Doping3应该设为1.05e13 cm^-3

## 详细说明

对于参数变化的物理解释：
* 增加Wtot可以提高耐压能力，但不要超过55 um
* 增加Wg能够改善栅极控制能力，建议控制在8-10 um之间
* Tdrift的增加有助于提高阳极电压

## 预期性能

如果采用以上参数，预计性能指标将改善如下：
```json
{
  "expected_results": {
    "vanode": 550,
    "latchup": true,
    "charge_collection": 8.5e-13,
    "energy_consumption": 3.2e-10
  },
  "improvement": {
    "vanode_increase": "12%",
    "energy_reduction": "8%"
  }
}
```

请根据以上建议调整参数进行下一轮模拟。
"""

    # 测试例2: 缺失部分建议值的情况
    test_string2 = """
# TCAD模拟优化建议

分析了迭代2的模拟结果后，我建议对以下参数进行调整：

| 参数 | 建议值 |
|------|--------|
| Wtot | 48.5 |
| Wg | 9.0 |
| Tdrift | ? |

关于Tdrift，我认为需要更多的模拟数据来确定最佳值。
但目前可以尝试设置Tox = 0.082。

其他参数可以保持不变。
"""

    # 测试例3: 同一参数有多个建议值的情况
    test_string3 = """
# 参数优化建议

分析结果表明，当前参数配置下性能不是最优的。我建议调整如下：

Wtot应该调整为50.5 um
但如果考虑到工艺限制，Wtot可以设为49.8 um

Wg的最佳值是9.5，但也可以接受9.3-9.7的范围。

对于Tdrift，建议先尝试330，如果效果不佳，可以降低到325。

Tox需要精确控制在0.08 um。
"""

    # 执行测试
    print("\n=== 测试例1: 复杂混合格式 ===")
    result1 = deepseek._parse_markdown_response(test_string1)
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    print("\n=== 测试例2: 缺失部分建议值 ===")
    result2 = deepseek._parse_markdown_response(test_string2)
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    print("\n=== 测试例3: 同一参数有多个建议值 ===")
    result3 = deepseek._parse_markdown_response(test_string3)
    print(json.dumps(result3, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_comprehensive_parsing() 