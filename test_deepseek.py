#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DeepSeek API的提交和获取功能
"""
import os
import sys
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入DeepSeek API模块
from auto_sim.deepseek_api import DeepSeekAPI

def main():
    """测试DeepSeek API"""
    print("开始测试DeepSeek API...")
    
    # 初始化API
    project_path = os.path.dirname(os.path.abspath(__file__))
    api = DeepSeekAPI(project_path)
    
    # 准备测试数据 - 当前参数
    current_params = {
        "Wtot": 50,
        "Wg": 10,
        "Wcp": 15,
        "Wcs": 4,
        "Tdrift": 320,
        "TPc": 0.2,
        "TNb": 1.5,
        "TNa": 1.5,
        "TPb": 5,
        "TPa": 0.6,
        "Tox": -0.2,
        "Tpoly": -2,
        "Tcathode": -4,
        "Zeropoint": 0,
        "Pc": 1e19,
        "Nb": 1.2e18,
        "Na": 1e15,
        "Ndrift": 5e13,
        "Npoly": 1e21,
        "Pb": 1e17,
        "Pa": 5e16,
        "x": 8.6,
        "Length": 35,
        "Vanode": 800,
        "angle": 90
    }
    
    # 准备测试数据 - 模拟仿真结果
    simulation_results = {
        "node_id": 53,
        "is_latchup": True,
        "vst_status": "闩锁电压为780V",
        "peak_current": 0.0032,
        "charge_collection": 1.4e-12,
        "energy_consumption": 2.8e-9
    }
    
    # 调用API获取优化建议
    print("\n1. 测试get_optimization_suggestions函数...")
    response = api.get_optimization_suggestions(
        iteration=1,
        params=current_params,
        simulation_results=simulation_results,
        sde_code="# 这里是SDE代码",
        sdevice_code="# 这里是SDevice代码"
    )
    
    # 打印结果
    print("\n获取到的优化建议:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    # 检查DeepSeek目录是否创建
    deepseek_prompts = Path(project_path) / "DeepSeek" / "Prompts"
    deepseek_responses = Path(project_path) / "DeepSeek" / "Responses"
    
    print(f"\n检查Prompt文件是否创建: {os.path.exists(deepseek_prompts)}")
    if os.path.exists(deepseek_prompts):
        print(f"Prompts目录中的文件: {os.listdir(deepseek_prompts)}")
    
    print(f"\n检查Response文件是否创建: {os.path.exists(deepseek_responses)}")
    if os.path.exists(deepseek_responses):
        print(f"Responses目录中的文件: {os.listdir(deepseek_responses)}")
    
    # 测试condense_experience函数
    print("\n2. 测试condense_experience函数...")
    condensed = api.condense_experience(1, 3)
    print(f"浓缩经验: {condensed}")
    
    print("\nDeepSeek API测试完成")

if __name__ == "__main__":
    main() 