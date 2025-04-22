#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek Markdown交互类测试脚本
测试使用Markdown格式进行API交互
"""

import os
import json
import logging
import random
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TestMarkdown')

# 导入DeepSeek Markdown交互类
from auto_sim.deepseek_markdown_interaction import DeepSeekMarkdownInteraction

def load_config(config_path: str = 'auto_sim_config.json'):
    """
    加载配置文件
    """
    logger.info(f"加载配置: {config_path}")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        return {}

def simulate_results(iteration: int) -> dict:
    """
    模拟生成结果数据
    """
    # 基础值
    base_latch_voltage = 750 + iteration * 30
    base_charge = 11.0 - iteration * 0.5
    base_energy = 1.3 - iteration * 0.1
    
    # 随机波动
    latch_voltage = base_latch_voltage + random.uniform(-10, 20)
    charge = max(5.0, base_charge + random.uniform(-0.3, 0.5))
    energy = max(0.5, base_energy + random.uniform(-0.1, 0.2))
    
    # 构造结果
    results = {
        "node_id": 50 + iteration,
        "latchup": latch_voltage < 900,
        "latch_voltage": latch_voltage,
        "peak_current": 0.45 + random.uniform(-0.05, 0.1),
        "charge_collection": charge,
        "energy_consumption": energy
    }
    
    return results

def main():
    """
    主函数
    """
    logger.info("开始测试 DeepSeek Markdown 交互")
    
    # 获取当前目录
    current_path = os.path.dirname(os.path.abspath(__file__))
    
    # 加载配置
    config = load_config()
    api_key = config.get('api_key', '')
    
    # 日志API密钥情况
    if api_key:
        logger.info(f"使用配置的API密钥: {api_key[:5]}...{api_key[-4:] if len(api_key) > 8 else ''}")
    else:
        logger.warning("未提供API密钥，将使用模拟响应")
    
    # 创建DeepSeek Markdown交互对象
    deepseek = DeepSeekMarkdownInteraction(
        project_path=current_path,
        api_key=api_key,
        use_simulation=False,  # 尝试使用真实API
        verbose=True
    )
    
    # 初始参数
    parameters = {
        "Wtot": 45.0,
        "Wg": 8.5,
        "Tdrift": 300.0,
        "Ndrift": 1.5e16,
        "Nwell": 3.0e17,
        "Nsub": 7.0e15,
        "Tox": 40.0,
        "Tpoly": 200.0,
        "Tcathode": 150.0
    }
    
    # 存储所有结果和参数
    all_results = []
    all_parameters = []
    
    # 执行多次迭代测试
    iterations = 3
    for i in range(1, iterations + 1):
        logger.info(f"\n{'='*50}\n迭代 {i}\n{'='*50}")
        
        # 模拟结果
        results = simulate_results(i)
        logger.info(f"模拟结果: {json.dumps(results, indent=2)}")
        
        # 保存当前参数和结果
        all_results.append(results)
        all_parameters.append(parameters.copy())
        
        # 获取优化建议
        logger.info(f"调用DeepSeek获取优化建议...")
        try:
            parameters = deepseek.get_optimization_suggestions(
                simulation_results=results,
                iteration=i,
                current_parameters=parameters
            )
            logger.info(f"获取到的优化参数: {json.dumps(parameters, indent=2)}")
        except Exception as e:
            logger.error(f"获取优化建议失败: {e}")
            break
    
    # 生成分析报告
    logger.info("\n生成所有迭代的分析报告")
    try:
        analysis_report = deepseek.analyze_simulation_results(
            all_results=all_results,
            all_parameters=all_parameters
        )
        logger.info(f"分析报告已生成，长度: {len(analysis_report)} 字符")
        
        # 显示报告的前200个字符
        preview = analysis_report[:200] + "..." if len(analysis_report) > 200 else analysis_report
        logger.info(f"报告预览:\n{preview}")
    except Exception as e:
        logger.error(f"生成分析报告失败: {e}")
    
    logger.info("DeepSeek Markdown 交互测试完成")

if __name__ == "__main__":
    main() 