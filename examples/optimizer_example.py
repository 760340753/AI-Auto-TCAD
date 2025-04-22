#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
参数优化示例脚本 - 演示如何使用ParameterOptimizer优化TCAD仿真参数
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_sim.parameter_optimizer import ParameterOptimizer
from auto_sim.result_analyzer import ResultAnalyzer

def main():
    """参数优化示例主函数"""
    print("Starting parameter optimization example")
    
    # 创建结果分析器
    result_analyzer = ResultAnalyzer()
    
    # 创建参数优化器
    optimizer = ParameterOptimizer(result_analyzer=result_analyzer)
    
    # 设置待优化参数 (参数名称: (最小值, 最大值, 步长))
    optimizer.set_parameters({
        'doping_concentration': (1e16, 1e18, 1e16),  # 掺杂浓度
        'gate_length': (0.13, 0.25, 0.01),          # 栅极长度
        'oxide_thickness': (2e-9, 5e-9, 0.5e-9)     # 氧化层厚度
    })
    
    # 定义目标函数
    def objective_function(analysis_result, parameters):
        """
        目标函数用于评估参数组合的性能
        在实际应用中，这应该基于真实的设备性能指标
        
        Args:
            analysis_result: 由结果分析器提供的分析结果
            parameters: 当前使用的参数值
        
        Returns:
            目标函数值 (越小越好)
        """
        # 在测试模式下，我们模拟一些结果
        # 在实际应用中，这些值应该来自仿真结果分析
        if not analysis_result:
            # 模拟分析结果
            gate_length = parameters['gate_length']
            doping = parameters['doping_concentration']
            oxide_thickness = parameters['oxide_thickness']
            
            # 模拟随机性能指标
            np.random.seed(int(gate_length * 1000 + doping / 1e15 + oxide_thickness * 1e10))
            
            # 模拟关键性能指标
            Ion = 500e-6 * (0.18 / gate_length) * np.sqrt(doping / 1e17) * (3e-9 / oxide_thickness) * (1 + 0.1 * np.random.randn())
            Ioff = 100e-12 * (gate_length / 0.18) * np.exp(-doping / 1e17) * (oxide_thickness / 3e-9) * (1 + 0.2 * np.random.randn())
            delay = 20e-12 * (gate_length / 0.18) * (oxide_thickness / 3e-9) * (1 + 0.05 * np.random.randn())
            
            # 模拟辐射性能指标
            LET_threshold = 25 * (doping / 2e17) * (gate_length / 0.18) * (1 + 0.1 * np.random.randn())
            cross_section = 1e-8 * (0.18 / gate_length) * np.sqrt(1e17 / doping) * (1 + 0.15 * np.random.randn())
            
            analysis_result = {
                'Ion': Ion,                     # 开态电流
                'Ioff': Ioff,                   # 关态电流
                'delay': delay,                 # 延迟时间
                'LET_threshold': LET_threshold, # LET阈值
                'cross_section': cross_section  # 截面积
            }
        
        # 计算目标函数 - 在这个例子中，我们希望：
        # 1. 最大化Ion/Ioff比率 (开关比)
        # 2. 最小化延迟
        # 3. 最大化LET阈值
        # 4. 最小化截面积
        
        Ion = analysis_result.get('Ion', 1e-6)
        Ioff = analysis_result.get('Ioff', 1e-12)
        delay = analysis_result.get('delay', 50e-12)
        LET_threshold = analysis_result.get('LET_threshold', 10)
        cross_section = analysis_result.get('cross_section', 1e-8)
        
        # 归一化因子，使不同性能指标的权重平衡
        Ion_Ioff_factor = -1.0   # 负号表示我们想最大化这个比率
        delay_factor = 2e10      # 归一化延迟(秒)的影响
        LET_factor = -0.05       # 负号表示我们想最大化LET阈值
        cs_factor = 1e8          # 归一化截面积(厘米²)的影响
        
        # 计算综合目标函数
        objective = (
            Ion_Ioff_factor * np.log10(Ion/Ioff) + 
            delay_factor * delay + 
            LET_factor * LET_threshold + 
            cs_factor * cross_section
        )
        
        return objective
    
    # 设置目标函数
    optimizer.set_objective_function(objective_function)
    
    # 运行优化 (在测试模式下)
    print("Running parameter optimization...")
    result = optimizer.optimize(method='differential_evolution', max_iterations=15)
    
    # 输出优化结果
    if result:
        print("\nOptimization Results:")
        print(f"Best parameters: {result['optimal_parameters']}")
        print(f"Objective value: {result['objective_value']:.4f}")
        print(f"Optimization success: {result['success']}")
        print(f"Number of iterations: {result['iterations']}")
        print(f"Execution time: {result['execution_time']:.2f} seconds")
        
        # 获取建议的下一组实验
        suggestions = optimizer.suggest_next_experiments(num_suggestions=2)
        
        print("\nSuggested Next Experiments:")
        for i, suggestion in enumerate(suggestions):
            print(f"\nSuggestion {i+1} ({suggestion['strategy']}):")
            print(f"Description: {suggestion['description']}")
            print("Parameters:")
            for param, value in suggestion['parameters'].items():
                print(f"  {param}: {value:.6g}")
    else:
        print("Optimization failed")
    
    print("\nParameter optimization example completed")


if __name__ == "__main__":
    main() 