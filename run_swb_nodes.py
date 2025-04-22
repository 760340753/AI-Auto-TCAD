#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行SWB节点脚本，简单处理器，用于swb_interaction中的_run_nodes_cmd方法
"""

import os
import sys
import json
import argparse
import logging
import time
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("run_nodes.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_nodes")

def run_nodes(nodes_file):
    """运行指定的节点"""
    try:
        # 读取节点文件
        with open(nodes_file, 'r') as f:
            node_ids = json.load(f)
        
        logger.info(f"从{nodes_file}读取节点ID: {node_ids}")
        
        # 模拟运行节点
        for node_id in node_ids:
            logger.info(f"正在运行节点 {node_id}...")
            # 模拟运行过程
            time.sleep(1)
            print(f"节点 {node_id} 开始运行")
        
        logger.info(f"成功运行所有节点: {node_ids}")
        return 0
    except Exception as e:
        logger.error(f"运行节点失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

def main():
    parser = argparse.ArgumentParser(description="运行Sentaurus节点")
    parser.add_argument("--nodes", required=True, help="节点ID文件路径")
    
    args = parser.parse_args()
    return run_nodes(args.nodes)

if __name__ == "__main__":
    sys.exit(main()) 
# -*- coding: utf-8 -*-
"""
运行SWB节点脚本，简单处理器，用于swb_interaction中的_run_nodes_cmd方法
"""

import os
import sys
import json
import argparse
import logging
import time
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("run_nodes.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_nodes")

def run_nodes(nodes_file):
    """运行指定的节点"""
    try:
        # 读取节点文件
        with open(nodes_file, 'r') as f:
            node_ids = json.load(f)
        
        logger.info(f"从{nodes_file}读取节点ID: {node_ids}")
        
        # 模拟运行节点
        for node_id in node_ids:
            logger.info(f"正在运行节点 {node_id}...")
            # 模拟运行过程
            time.sleep(1)
            print(f"节点 {node_id} 开始运行")
        
        logger.info(f"成功运行所有节点: {node_ids}")
        return 0
    except Exception as e:
        logger.error(f"运行节点失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

def main():
    parser = argparse.ArgumentParser(description="运行Sentaurus节点")
    parser.add_argument("--nodes", required=True, help="节点ID文件路径")
    
    args = parser.parse_args()
    return run_nodes(args.nodes)

if __name__ == "__main__":
    sys.exit(main()) 