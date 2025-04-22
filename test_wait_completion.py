#!/usr/bin/env python3
# 测试wait_for_simulation_completion方法

import logging
import time
import sys
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test")

# 导入自动化仿真模块
sys.path.append('.')
from auto_sim.auto_sim_main import AutoSimulation
from auto_sim.swb_interaction import SWBInteraction

def main():
    """测试wait_for_simulation_completion方法"""
    logger.info("开始测试wait_for_simulation_completion方法")
    
    # 初始化对象
    project_path = Path('.')
    swb = SWBInteraction(project_path)
    
    # 获取当前节点信息
    current_nodes = []
    for node_file in project_path.glob("n*_dvs.cmd"):
        try:
            node_id = int(node_file.stem.split('_')[0][1:])
            current_nodes.append(node_id)
        except (ValueError, IndexError):
            continue
    
    if not current_nodes:
        logger.error("未找到任何节点文件")
        return
    
    # 选择最后一个节点进行测试
    test_node = max(current_nodes)
    logger.info(f"将测试节点: {test_node}")
    
    # 初始化AutoSimulation对象
    auto_sim = AutoSimulation(str(project_path), max_iterations=1, use_fake_results=False)
    
    # 测试wait_for_simulation_completion方法
    logger.info(f"开始等待节点 {test_node} 完成")
    start_time = time.time()
    completed_nodes, failed_nodes = auto_sim.wait_for_simulation_completion([test_node], timeout=60)
    end_time = time.time()
    
    # 输出结果
    logger.info(f"等待完成，耗时: {end_time - start_time:.2f}秒")
    logger.info(f"完成的节点: {completed_nodes}")
    logger.info(f"失败的节点: {failed_nodes}")
    
    # 节点状态
    status = auto_sim.swb_interaction.get_node_status(test_node)
    logger.info(f"节点 {test_node} 当前状态: {status}")
    
    # 如果节点已完成，尝试解析结果
    if test_node in completed_nodes:
        logger.info(f"尝试解析节点 {test_node} 的结果")
        try:
            results = auto_sim.swb_interaction.parse_simulation_results(test_node)
            logger.info(f"解析结果: {results}")
        except Exception as e:
            logger.error(f"解析结果失败: {str(e)}")
    
    logger.info("测试完成")

if __name__ == "__main__":
    main() 