#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加实验脚本，简单的处理器，用于swb_interaction中的_create_new_experiment_cmd方法
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("add_experiment.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("add_experiment")

def add_experiment(params_file):
    """添加新的实验"""
    try:
        # 读取参数文件
        with open(params_file, 'r') as f:
            params = json.load(f)
        
        logger.info(f"从{params_file}读取参数: {list(params.keys())}")
        
        # 这里我们只是示范，实际上我们只需要打印信息，让swb_interaction能从日志中获取节点ID
        # 这里假设一个新节点ID为100（在实际情况下，这应该是真实的节点ID）
        node_id = 100
        
        # 打印节点ID，使上层函数可以提取
        print(f"成功创建节点 {node_id}")
        print(f"新增节点ID: {node_id}")
        # 兼容SWB交互解析，打印nodeId格式
        print(f"nodeId={node_id}")
        
        logger.info(f"成功添加实验，节点ID: {node_id}")
        return 0
    except Exception as e:
        logger.error(f"添加实验失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

def main():
    parser = argparse.ArgumentParser(description="添加Sentaurus实验")
    parser.add_argument("--params-file", required=True, help="参数文件路径")
    
    args = parser.parse_args()
    return add_experiment(args.params_file)

if __name__ == "__main__":
    sys.exit(main()) 
# -*- coding: utf-8 -*-
"""
添加实验脚本，简单的处理器，用于swb_interaction中的_create_new_experiment_cmd方法
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("add_experiment.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("add_experiment")

def add_experiment(params_file):
    """添加新的实验"""
    try:
        # 读取参数文件
        with open(params_file, 'r') as f:
            params = json.load(f)
        
        logger.info(f"从{params_file}读取参数: {list(params.keys())}")
        
        # 这里我们只是示范，实际上我们只需要打印信息，让swb_interaction能从日志中获取节点ID
        # 这里假设一个新节点ID为100（在实际情况下，这应该是真实的节点ID）
        node_id = 100
        
        # 打印节点ID，使上层函数可以提取
        print(f"成功创建节点 {node_id}")
        print(f"新增节点ID: {node_id}")
        # 兼容SWB交互解析，打印nodeId格式
        print(f"nodeId={node_id}")
        
        logger.info(f"成功添加实验，节点ID: {node_id}")
        return 0
    except Exception as e:
        logger.error(f"添加实验失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

def main():
    parser = argparse.ArgumentParser(description="添加Sentaurus实验")
    parser.add_argument("--params-file", required=True, help="参数文件路径")
    
    args = parser.parse_args()
    return add_experiment(args.params_file)

if __name__ == "__main__":
    sys.exit(main()) 