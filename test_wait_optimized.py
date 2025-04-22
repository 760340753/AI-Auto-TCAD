#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
from pathlib import Path

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自动化仿真主类
from auto_sim.auto_sim_main import AutoSimulation

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """测试优化后的节点等待方法"""
    
    # 使用当前目录作为项目路径
    project_path = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # 初始化自动化仿真对象
    auto_sim = AutoSimulation(project_path=project_path)
    
    # 使用固定的节点ID列表
    node_ids = [54, 55, 56, 57, 58]
    
    logger.info(f"测试节点: {node_ids}")
    logger.info(f"总测试节点数: {len(node_ids)}")
    
    # 记录开始时间
    start_time = time.time()
    
    # 调用优化后的等待方法，设置较短的超时时间
    node_status = auto_sim.wait_for_simulation_completion(node_ids, timeout=60)
    
    # 记录完成时间和耗时
    elapsed_time = time.time() - start_time
    logger.info(f"等待完成，耗时 {elapsed_time:.2f} 秒")
    
    # 打印结果
    logger.info("节点状态结果:")
    for node_id, status in node_status.items():
        logger.info(f"节点 {node_id}: {status}")
    
    # 统计结果
    done_count = list(node_status.values()).count("done")
    failed_count = list(node_status.values()).count("failed")
    other_count = len(node_status) - done_count - failed_count
    
    logger.info(f"完成: {done_count}, 失败: {failed_count}, 其他: {other_count}")
    logger.info(f"完成率: {done_count/len(node_status)*100:.1f}%")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 