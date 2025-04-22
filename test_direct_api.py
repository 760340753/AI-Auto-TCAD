#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试DeepSeekInteraction类的API调用
"""
import os
import sys
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入DeepSeekInteraction类
from auto_sim.deepseek_interaction import DeepSeekInteraction

def main():
    """直接测试API调用"""
    print("开始直接测试DeepSeek API调用...")
    
    # 初始化DeepSeekInteraction对象
    api_key = "sk-buspthftjrkhcudljfardlbubjlmpfoxehgstdipajrxpccc"
    interaction = DeepSeekInteraction(api_key=api_key)
    
    # 准备测试消息
    messages = [
        {"role": "system", "content": "你是一位半导体器件物理和辐射效应专家，熟悉TCAD仿真和SEE效应。"},
        {"role": "user", "content": "请简要分析在TCAD仿真中，掺杂浓度和栅极长度对单粒子效应的影响。"}
    ]
    
    print("\n直接调用_call_api方法...")
    try:
        response = interaction._call_api(messages)
        
        print("\n获取到的API响应:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        print("\nAPI调用成功!")
    except Exception as e:
        print(f"\nAPI调用失败: {str(e)}")
    
    print("\n测试完成")

if __name__ == "__main__":
    main() 