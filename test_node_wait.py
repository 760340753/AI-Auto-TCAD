#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import json
from pathlib import Path

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自动化仿真主类
from auto_sim.auto_sim_main import AutoSimulation

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_node_wait():
    """测试节点等待功能"""
    
    # 使用当前目录作为项目路径
    project_path = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # 初始化自动化仿真对象
    auto_sim = AutoSimulation(project_path=project_path)
    
    # 测试数据：包含已知参数节点和计算节点
    test_nodes = [55, 56, 57, 58, 59]  # 前三个是已知参数节点
    
    logger.info("=" * 50)
    logger.info("开始测试节点等待功能")
    logger.info(f"测试节点: {test_nodes}")
    
    # 调用等待方法
    result = auto_sim.wait_for_simulation_completion(test_nodes, timeout=60)
    
    logger.info(f"等待结果: {result}")
    logger.info("=" * 50)
    
    return result

if __name__ == "__main__":
    try:
        test_result = test_node_wait()
        print(f"测试完成，结果: {test_result}")
        sys.exit(0 if test_result else 1)
    except Exception as e:
        logger.exception("测试过程中发生异常")
        print(f"测试失败: {str(e)}")
        sys.exit(1) 