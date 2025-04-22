#!/usr/bin/env python3
# 测试完整的工作流程

import logging
import sys
import time
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
from auto_sim.parameter_manager import ParameterManager

def main():
    """测试完整的工作流程"""
    logger.info("开始测试完整工作流程")
    
    # 初始化对象
    project_path = Path('.')
    
    # 先创建一个SWBInteraction实例，检查项目状态
    swb = SWBInteraction(project_path)
    swb.initialize_swb_connection()
    
    # 1. 获取当前节点
    old_nodes = []
    for node_file in project_path.glob("n*_dvs.cmd"):
        try:
            node_id = int(node_file.stem.split('_')[0][1:])
            old_nodes.append(node_id)
        except (ValueError, IndexError):
            continue
    
    logger.info(f"当前已有节点: {sorted(old_nodes)}")
    
    # 2. 创建测试参数
    test_params = {
        "Wtot": 51,
        "Wg": 11,
        "Wcp": 15,
        "Wcs": 4,
        "Tdrift": 330,
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
        "Length": 35
    }
    
    # 3. 创建新实验
    logger.info("创建新实验")
    new_nodes = swb.create_new_experiment(test_params)
    logger.info(f"创建的新节点: {new_nodes}")
    
    if not new_nodes:
        logger.error("未能创建新节点，测试失败")
        return
    
    node_id = new_nodes[0]
    logger.info(f"将使用节点ID: {node_id}")
    
    # 4. 运行节点
    logger.info(f"运行节点: {node_id}")
    run_results = swb.run_nodes([node_id])
    logger.info(f"运行结果: {run_results}")
    
    # 5. 等待节点完成
    logger.info("等待节点完成")
    
    # 初始化AutoSimulation对象（对于wait_for_simulation_completion方法）
    auto_sim = AutoSimulation(str(project_path), max_iterations=1, use_fake_results=False)
    
    # 设置较短的超时时间，以便测试不会卡住
    completed_nodes, failed_nodes = auto_sim.wait_for_simulation_completion([node_id], timeout=30)
    
    logger.info(f"等待结果 - 完成的节点: {completed_nodes}, 失败的节点: {failed_nodes}")
    
    # 6. 解析结果
    if node_id in completed_nodes:
        logger.info(f"尝试解析节点 {node_id} 的结果")
        try:
            results = swb.parse_simulation_results(node_id)
            logger.info(f"解析结果: {results}")
        except Exception as e:
            logger.error(f"解析结果失败: {str(e)}")
    else:
        logger.warning(f"节点 {node_id} 未完成，跳过结果解析")
    
    # 7. 检查节点状态一次
    status = swb.get_node_status(node_id)
    logger.info(f"最终节点状态: {status}")
    
    # 8. 关闭连接
    swb.close_connection()
    logger.info("测试完成")

if __name__ == "__main__":
    main() 