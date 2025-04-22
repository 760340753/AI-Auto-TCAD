#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import json
import argparse
from pathlib import Path

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自动化仿真模块
from auto_sim.parameter_manager import ParameterManager
from auto_sim.swb_interaction import SWBInteraction

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_create_node(method="api", use_backup=False):
    """
    测试节点创建功能
    
    Args:
        method: 创建方法，"api"或"cmd"
        use_backup: 是否直接使用备用方法
        
    Returns:
        bool: 成功标志
    """
    # 使用当前目录作为项目路径
    project_path = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # 初始化参数管理器
    param_manager = ParameterManager(project_path)
    
    # 获取初始参数
    params = param_manager.get_initial_params()
    if not params:
        logger.error("无法获取初始参数")
        return False
    
    logger.info(f"使用参数: {params}")
    
    # 初始化SWB交互对象
    swb = SWBInteraction(project_path)
    
    # 尝试初始化SWB连接
    if method == "api" and not use_backup:
        swb.initialize_swb_connection()
    
    # 扫描当前节点
    logger.info("扫描项目目录中的节点文件...")
    node_files = list(project_path.glob("n*_des.cmd"))
    existing_node_ids = [int(f.stem.split('_')[0][1:]) for f in node_files]
    logger.info(f"当前存在节点: {sorted(existing_node_ids)}")
    
    # 创建新实验
    logger.info(f"使用 {method} 方法创建新实验...")
    
    if method == "api" and not use_backup:
        # 使用API方法
        success, new_nodes = swb.create_new_experiment(params)
    else:
        # 使用命令行方法
        success, new_nodes = swb._create_new_experiment_cmd(params)
    
    if success:
        logger.info(f"创建成功，新增节点: {new_nodes}")
        
        # 检查是否确实创建了新节点
        new_node_files = list(project_path.glob("n*_des.cmd"))
        current_node_ids = [int(f.stem.split('_')[0][1:]) for f in new_node_files]
        actually_added = set(current_node_ids) - set(existing_node_ids)
        
        logger.info(f"通过文件系统确认的新增节点: {actually_added}")
        if actually_added:
            if new_nodes == actually_added:
                logger.info("节点识别正确")
            else:
                logger.warning(f"节点识别不完全匹配。报告: {new_nodes}, 实际: {actually_added}")
        else:
            logger.warning("未通过文件系统确认到新增节点")
            
        return True
    else:
        logger.error("创建失败")
        return False
        
def main():
    parser = argparse.ArgumentParser(description="测试节点创建功能")
    parser.add_argument("--method", choices=["api", "cmd"], default="api", help="创建方法")
    parser.add_argument("--use-backup", action="store_true", help="直接使用备用方法")
    args = parser.parse_args()
    
    try:
        success = test_create_node(args.method, args.use_backup)
        exit_code = 0 if success else 1
        print(f"\n测试{'成功' if success else '失败'}")
        return exit_code
    except Exception as e:
        logger.exception("测试过程中发生异常")
        print(f"测试异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 