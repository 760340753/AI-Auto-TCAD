#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果分析器模块

处理模拟结果，提取关键数据，例如闩锁状态、电压、电流等
"""
import os
import re
import json
import logging
import random
from pathlib import Path
from typing import Optional

# 获取日志记录器
logger = logging.getLogger("auto_sim.result_analyzer")

class ResultAnalyzer:
    """仿真结果分析器"""
    
    def __init__(self, project_path):
        """
        初始化结果分析器
        
        Args:
            project_path: 项目根目录
        """
        self.project_path = Path(project_path)
        
        # 创建结果目录
        self.extracted_dir = self.project_path / "Results" / "Extracted"
        self.raw_dir = self.project_path / "Results" / "Raw"
        self.figures_dir = self.project_path / "Results" / "Figures"
        
        os.makedirs(self.extracted_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)
        
        logger.info(f"结果分析器初始化，项目路径: {project_path}")
    
    def _find_relevant_plt(self, node_id: int, tool_label: str) -> Optional[Path]:
        """根据节点ID和工具标签查找最相关的 PLT 文件"""
        # 优先查找包含工具标签的文件名
        patterns_with_label = [
            f"{tool_label}_n{node_id}_des.plt",
            f"{tool_label}_n{node_id}_dvs.plt", # SDE uses dvs
            f"*_n{node_id}*_{tool_label.lower()}*.plt" # 更通用的模式
        ]
        
        for pattern in patterns_with_label:
            found = list(self.project_path.glob(pattern))
            if found:
                logger.info(f"找到与标签 '{tool_label}' 相关的 PLT: {found[0]}")
                return found[0]
                
        # 如果按标签找不到，则使用通用模式查找
        generic_pattern = f"*n{node_id}*.plt"
        found_generic = list(self.project_path.glob(generic_pattern))
        if found_generic:
            logger.warning(f"未找到带标签 '{tool_label}' 的 PLT，使用通用模式找到: {found_generic[0]}")
            return found_generic[0]
            
        logger.error(f"无法为节点 {node_id} (工具: {tool_label}) 找到任何 PLT 文件")
        return None

    def process_simulation_results(self, node_id: int, tool_label: str, mode=None):
        """
        处理仿真结果，根据工具标签解析不同数据。
        
        Args:
            node_id: 节点ID
            tool_label: 工具标签 (例如 'BV', 'IcVc', 'IdVg')
            mode: 处理模式，'fake'表示使用假结果
            
        Returns:
            dict: 处理后的结果 (可能包含 breakdown_voltage, threshold_voltage 等)
        """
        if mode == "fake":
            return self._generate_fake_result(tool_label)
            
        try:
            plt_file = self._find_relevant_plt(node_id, tool_label)
            if not plt_file:
                return self._generate_basic_result(node_id, tool_label)
                
            logger.info(f"开始解析 PLT 文件: {plt_file}")
            
            # 根据工具标签调用不同的解析逻辑
            if tool_label.upper() == 'BV':
                results = self._parse_bv_results(plt_file)
            elif tool_label.upper() == 'ICVC':
                results = self._parse_icvc_results(plt_file)
            elif tool_label.upper() == 'IDVG': # 假设是 IdVg
                results = self._parse_idvg_results(plt_file)
            else:
                logger.warning(f"未知的工具标签 '{tool_label}'，执行通用解析。")
                results = self._parse_generic_results(plt_file)
                
            # 添加节点 ID 和工具标签到结果中，方便追踪
            results['parsed_node_id'] = node_id
            results['parsed_tool_label'] = tool_label
            
            logger.info(f"节点 {node_id} ({tool_label}) 解析结果: {results}")
            return results
            
        except Exception as e:
            logger.error(f"处理节点 {node_id} ({tool_label}) 的结果时出错: {str(e)}")
            logger.error(traceback.format_exc())
            return self._generate_basic_result(node_id, tool_label)

    def _parse_bv_results(self, plt_file: Path) -> dict:
        """解析击穿电压 (BV) 结果"""
        results = {'breakdown_voltage': 0.0, 'leakage_current': 0.0}
        try:
            with open(plt_file, 'r') as f:
                content = f.read()
                # 查找击穿电压 (示例正则，需要根据实际 plt 文件格式调整)
                bv_match = re.search(r"Breakdown Voltage:\s*([\d\.]+)", content, re.IGNORECASE)
                if bv_match:
                    results['breakdown_voltage'] = float(bv_match.group(1))
                else:
                    # 如果没有明确的击穿电压标签，可能需要从数据点中推断
                    # 例如，找到电流急剧增加时的阳极电压
                    logger.warning(f"无法在 {plt_file.name} 中找到明确的击穿电压标签，返回 0")
                    
                # 查找漏电流 (示例正则)
                leakage_match = re.search(r"Leakage Current at BV:\s*([\d\.eE\+\-]+)", content, re.IGNORECASE)
                if leakage_match:
                    results['leakage_current'] = float(leakage_match.group(1))
                    
        except Exception as e:
            logger.error(f"解析 BV PLT 文件 {plt_file.name} 出错: {e}")
        return results

    def _parse_icvc_results(self, plt_file: Path) -> dict:
        """解析正向导通 (IcVc) 结果"""
        results = {'on_state_voltage': 0.0, 'on_state_current': 0.0}
        # TODO: 实现 IcVc 解析逻辑 (例如，查找特定电流下的 Vce_sat)
        logger.warning(f"IcVc 解析逻辑尚未实现 ({plt_file.name})，返回默认值。")
        return results

    def _parse_idvg_results(self, plt_file: Path) -> dict:
        """解析阈值电压 (IdVg/IcVg) 结果"""
        results = {'threshold_voltage': float('inf'), 'max_transconductance': 0.0}
        try:
            with open(plt_file, 'r') as f:
                content = f.read()
                # 查找阈值电压 (示例正则，需要根据实际 plt 文件格式调整)
                vth_match = re.search(r"Threshold Voltage Vth\s*@.*?=\s*([\d\.]+)", content, re.IGNORECASE)
                if vth_match:
                    results['threshold_voltage'] = float(vth_match.group(1))
                else:
                    # 如果没有明确标签，可能需要从数据点推断 (例如，线性外推法)
                    logger.warning(f"无法在 {plt_file.name} 中找到明确的阈值电压标签，返回 inf")
                
                # 查找跨导等其他参数 (示例)
                gm_match = re.search(r"Max Transconductance gm:\s*([\d\.eE\+\-]+)", content, re.IGNORECASE)
                if gm_match:
                    results['max_transconductance'] = float(gm_match.group(1))

        except Exception as e:
            logger.error(f"解析 IdVg PLT 文件 {plt_file.name} 出错: {e}")
            # 出错时确保返回默认的 inf，避免检查目标时误判
            results['threshold_voltage'] = float('inf') 
        return results

    def _parse_generic_results(self, plt_file: Path) -> dict:
        """通用解析逻辑 (备用)"""
        logger.warning(f"执行通用 PLT 解析 ({plt_file.name})，可能不准确。")
        # 尝试提取常用指标
        results = {}
        try:
             # 可以加入一些通用的正则，尝试匹配常见指标
             pass
        except Exception as e:
             logger.error(f"通用 PLT 解析失败: {e}")
        return results
            
    def _generate_fake_result(self, tool_label:str = 'unknown'):
        """生成假的结果数据（用于测试），根据工具标签生成不同指标"""
        import random
        base_result = {
            'peak_current': random.uniform(0.01, 1.0),
            'charge_collection': random.uniform(0.5, 10.0),
            'energy_consumption': random.uniform(1.0, 20.0)
        }
        if tool_label.upper() == 'BV':
            base_result['breakdown_voltage'] = random.uniform(1300, 1600)
            base_result['leakage_current'] = random.uniform(1e-9, 1e-6)
        elif tool_label.upper() == 'IDVG':
            base_result['threshold_voltage'] = random.uniform(4, 12)
        elif tool_label.upper() == 'ICVC':
            base_result['on_state_voltage'] = random.uniform(1.5, 3.0)
        else: # 默认或未知
            is_latchup = random.random() > 0.5
            base_result['is_latchup'] = is_latchup
            base_result['vanode'] = random.uniform(100, 900)
            base_result['vst_status'] = "闩锁" if is_latchup else "未闩锁"
            
        return base_result
        
    def _generate_basic_result(self, node_id, tool_label: str = 'unknown'):
        """生成基本结果（当无法找到或解析PLT文件时）"""
        logger.info(f"为节点 {node_id} ({tool_label}) 生成基本结果（无或无法解析PLT文件）")
        
        base_result = {
            'peak_current': 0.05,
            'charge_collection': 1.0,
            'energy_consumption': 5.0,
            'vst_status': "未知（无/错误PLT文件）",
            'is_simulated': False, # 标记为非有效结果
            'error': f"无法找到或解析节点 {node_id} ({tool_label}) 的 PLT 文件"
        }
        if tool_label.upper() == 'BV':
             base_result['breakdown_voltage'] = 0.0
        elif tool_label.upper() == 'IDVG':
             base_result['threshold_voltage'] = float('inf')
        # ... 其他工具可以添加默认错误值 ...
             
        return base_result 