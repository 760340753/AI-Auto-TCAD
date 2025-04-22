#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动仿真完整流程
使用假仿真结果模拟整个流程
"""
import os
import sys
import time
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自动仿真主控模块
from auto_sim.auto_sim_main import AutoSimulation

def main():
    """测试自动仿真流程"""
    print("\n======= 测试自动仿真流程 =======")
    
    # 项目路径
    project_path = os.path.dirname(os.path.abspath(__file__))
    print(f"项目路径: {project_path}")
    
    # 配置
    config = {
        "use_fake_results": True,  # 使用假结果
        "max_iterations": 3,       # 最大迭代次数
        "skip_confirmation": True, # 跳过确认
        "performance_target": {
            "VST": 700              # 性能目标
        }
    }
    
    # 打印配置
    print("\n配置:")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    # 初始化自动仿真系统
    print("\n初始化自动仿真系统...")
    auto_sim = AutoSimulation(
        project_path=project_path,
        max_iterations=config.get("max_iterations", 10),
        api_key=None,  # 不使用真实API
        use_fake_results=config.get("use_fake_results", True)
    )
    
    # 跳过确认
    if config.get("skip_confirmation", False):
        print("跳过参数确认...")
        auto_sim.verify_initial_parameters = lambda: True
    
    # 设置性能目标
    if "performance_target" in config:
        auto_sim.performance_target = config["performance_target"]
        print(f"设置性能目标: {auto_sim.performance_target}")
    
    # 运行自动仿真流程
    print("\n开始运行自动仿真流程...")
    start_time = time.time()
    
    success = auto_sim.run_complete_flow()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 打印结果
    print("\n======= 自动仿真流程结束 =======")
    print(f"耗时: {elapsed_time:.2f}秒")
    
    if success:
        print("\n自动仿真流程成功!")
        best_result = auto_sim.get_best_result_so_far()
        if best_result:
            print(f"最佳结果: 迭代{best_result['iteration']}, 阳极电压={best_result.get('vanode', 'N/A')}V")
            print(f"请查看最终报告获取详细信息: {project_path}/Reports/final_report.md")
        else:
            print("未找到满足性能目标的结果")
    else:
        print("\n自动仿真流程失败!")
        print(f"请查看错误报告: {project_path}/Reports/error_report.md")
    
    # 清理资源
    auto_sim.cleanup()
    
    print("\n测试完成.")

if __name__ == "__main__":
    main() 