#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DeepSeekMarkdownInteraction类
用于测试DeepSeek API的Markdown格式交互
"""

import os
import sys
import json
import logging
import time
import random
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("markdown_test")

# 导入DeepSeekMarkdownInteraction类
sys.path.append(os.path.join(os.path.dirname(__file__), 'auto_sim'))
from deepseek_markdown_interaction import DeepSeekMarkdownInteraction

def load_config(config_path: str = 'auto_sim_config.json') -> dict:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    logger.info(f"加载配置文件: {config_path}")
    try:
        if not os.path.exists(config_path):
            logger.error(f"配置文件不存在: {config_path}")
            return {}
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"成功加载配置文件")
            return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return {}

def simulate_results(iteration: int) -> dict:
    """
    生成模拟的仿真结果
    
    Args:
        iteration: 当前迭代次数
        
    Returns:
        仿真结果字典
    """
    # 基准值
    base_voltage = 750 + random.randint(-50, 50)
    base_current = 25 + random.random() * 5
    base_charge = 100 + random.random() * 10
    base_energy = 250 + random.random() * 25
    
    # 根据迭代次数调整值
    improvement = min(0.03 * iteration, 0.15)  # 最多提升15%
    
    # 计算最终值
    latch_voltage = base_voltage * (1 + improvement * random.uniform(0.5, 1.5))
    peak_current = base_current * (1 - improvement * random.uniform(0.3, 1.0))
    charge_collection = base_charge * (1 - improvement * random.uniform(0.4, 1.2))
    energy_consumption = base_energy * (1 - improvement * random.uniform(0.5, 1.3))
    
    # 构建结果字典
    results = {
        "node_id": 50 + iteration,
        "latchup": True,
        "latch_voltage": latch_voltage,
        "peak_current": peak_current,
        "charge_collection": charge_collection,
        "energy_consumption": energy_consumption
    }
    
    return results

def main():
    """主函数"""
    logger.info("开始测试DeepSeekMarkdownInteraction")
    
    # 获取当前目录作为项目路径
    project_path = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"项目路径: {project_path}")
    
    # 加载配置
    config = load_config()
    if not config:
        logger.error("无法加载配置，使用默认设置")
    
    # 获取API密钥
    api_key = config.get("deepseek_api_key", "")
    logger.info(f"API密钥: {'已设置' if api_key else '未设置，将使用模拟响应'}")
    
    # 初始化DeepSeekMarkdownInteraction
    ds_interaction = DeepSeekMarkdownInteraction(
        project_path=project_path,
        api_key=api_key,
        use_simulation=not bool(api_key),  # 如果没有API密钥，使用模拟响应
        verbose=True
    )
    logger.info("初始化DeepSeekMarkdownInteraction完成")
    
    # 初始参数
    current_parameters = {
        "Wtot": 50.0,
        "Wg": 9.0,
        "Tdrift": 320.0,
        "Ndrift": 1.8e16,
        "Nwell": 3.5e17,
        "Nsub": 6.5e15,
        "Tox": 42.0,
        "Tpoly": 210.0,
        "Tcathode": 155.0
    }
    
    # 存储所有迭代的参数和结果
    all_parameters = [current_parameters.copy()]
    all_results = []
    
    # 运行3轮迭代
    for iteration in range(1, 4):
        logger.info(f"===== 开始第{iteration}轮迭代 =====")
        
        # 生成模拟结果
        simulation_results = simulate_results(iteration)
        logger.info(f"模拟结果生成完成: 闩锁电压={simulation_results['latch_voltage']:.2f}, 峰值电流={simulation_results['peak_current']:.2f}")
        
        # 保存结果
        all_results.append(simulation_results)
        
        # 获取优化建议
        logger.info(f"请求参数优化建议")
        optimized_parameters = ds_interaction.get_optimization_suggestions(
            simulation_results=simulation_results,
            iteration=iteration,
            current_parameters=current_parameters
        )
        
        # 打印优化后的参数
        logger.info(f"优化建议获取完成")
        for key, value in optimized_parameters.items():
            old_value = current_parameters.get(key, 0)
            change_percent = ((value - old_value) / old_value * 100) if old_value != 0 else 0
            logger.info(f"参数 {key}: {old_value:.2f} -> {value:.2f} ({change_percent:+.2f}%)")
        
        # 更新当前参数
        current_parameters = optimized_parameters
        all_parameters.append(current_parameters.copy())
        
        # 模拟迭代间隔
        if iteration < 3:
            wait_time = random.randint(1, 3)
            logger.info(f"等待{wait_time}秒后开始下一轮迭代...")
            time.sleep(wait_time)
    
    # 生成分析报告
    logger.info("生成仿真结果分析报告")
    report = ds_interaction.analyze_simulation_results(all_results, all_parameters)
    logger.info("分析报告生成完成")
    
    # 输出报告位置
    report_file = Path(project_path) / "DeepSeek" / "Reports" / "analysis_report.md"
    logger.info(f"报告已保存至: {report_file}")
    
    # 测试完成
    logger.info("DeepSeekMarkdownInteraction测试完成")

if __name__ == "__main__":
    main() 