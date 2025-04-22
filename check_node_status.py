#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查SWB节点状态脚本，简单处理器，用于swb_interaction中的_check_run_status_files方法
"""

import os
import sys
import json
import argparse
import logging
import random
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("check_status.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("check_status")

def check_node_status(nodes_file):
    """检查指定节点的状态"""
    try:
        # 读取节点文件
        with open(nodes_file, 'r') as f:
            node_ids = json.load(f)
        
        logger.info(f"从{nodes_file}读取节点ID: {node_ids}")
        
        # 模拟节点状态
        status = {}
        statuses = ["done", "running", "failed", "ready"]
        weights = [0.7, 0.1, 0.1, 0.1]  # 大多数节点为完成状态
        
        for node_id in node_ids:
            # 模拟70%的节点已完成
            status[str(node_id)] = random.choices(statuses, weights=weights)[0]
            logger.info(f"节点 {node_id} 状态: {status[str(node_id)]}")
            print(f"节点 {node_id} 状态: {status[str(node_id)]}")
        
        # 输出到指定文件
        output_file = nodes_file.replace(".json", "_status.json")
        with open(output_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info(f"节点状态已写入: {output_file}")
        return 0
    except Exception as e:
        logger.error(f"检查节点状态失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

def main():
    parser = argparse.ArgumentParser(description="检查Sentaurus节点状态")
    parser.add_argument("--nodes", required=True, help="节点ID文件路径")
    
    args = parser.parse_args()
    return check_node_status(args.nodes)

if __name__ == "__main__":
    sys.exit(main()) 
# -*- coding: utf-8 -*-
"""
检查SWB节点状态脚本，简单处理器，用于swb_interaction中的_check_run_status_files方法
"""

import os
import sys
import json
import argparse
import logging
import random
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("check_status.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("check_status")

def check_node_status(nodes_file):
    """检查指定节点的状态"""
    try:
        # 读取节点文件
        with open(nodes_file, 'r') as f:
            node_ids = json.load(f)
        
        logger.info(f"从{nodes_file}读取节点ID: {node_ids}")
        
        # 模拟节点状态
        status = {}
        statuses = ["done", "running", "failed", "ready"]
        weights = [0.7, 0.1, 0.1, 0.1]  # 大多数节点为完成状态
        
        for node_id in node_ids:
            # 模拟70%的节点已完成
            status[str(node_id)] = random.choices(statuses, weights=weights)[0]
            logger.info(f"节点 {node_id} 状态: {status[str(node_id)]}")
            print(f"节点 {node_id} 状态: {status[str(node_id)]}")
        
        # 输出到指定文件
        output_file = nodes_file.replace(".json", "_status.json")
        with open(output_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info(f"节点状态已写入: {output_file}")
        return 0
    except Exception as e:
        logger.error(f"检查节点状态失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

def main():
    parser = argparse.ArgumentParser(description="检查Sentaurus节点状态")
    parser.add_argument("--nodes", required=True, help="节点ID文件路径")
    
    args = parser.parse_args()
    return check_node_status(args.nodes)

if __name__ == "__main__":
    sys.exit(main()) 