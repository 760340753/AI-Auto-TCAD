#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeekMarkdownInteraction类
用于与DeepSeek API交互并处理Markdown格式的请求和响应
"""

import os
import json
import time
import logging
import random
import requests
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class DeepSeekMarkdownInteraction:
    """
    DeepSeekMarkdownInteraction类
    用于与DeepSeek API交互，使用Markdown格式进行通信
    功能：
    1. 调用DeepSeek API获取优化建议
    2. 解析Markdown格式的响应
    3. 将请求和响应保存到文件中
    4. 生成结果分析报告
    """

    def __init__(
        self,
        project_path: str,
        api_key: str = "",
        model: str = "Pro/deepseek-ai/DeepSeek-R1",
        use_simulation: bool = False,
        max_retries: int = 3,
        timeout: int = 120,
        temperature: float = 0.01,
        verbose: bool = False
    ):
        """
        初始化DeepSeekMarkdownInteraction类
        
        Args:
            project_path: 项目路径
            api_key: DeepSeek API密钥
            model: 使用的模型名称
            use_simulation: 是否使用模拟响应（调试用）
            max_retries: 最大重试次数
            timeout: API超时时间（秒）
            temperature: 模型温度参数
            verbose: 是否输出详细日志
        """
        self.project_path = project_path
        self.api_key = api_key
        self.model = model
        self.use_simulation = use_simulation
        self.max_retries = max_retries
        self.timeout = timeout
        self.temperature = temperature
        self.verbose = verbose
        
        # 创建必要的目录
        self._create_directories()
        
        logger.info(f"初始化DeepSeekMarkdownInteraction完成 - 模型: {model}")
        if use_simulation:
            logger.info("使用模拟响应模式")
        else:
            masked_key = f"{api_key[:4]}...{api_key[-4:]}" if api_key and len(api_key) > 8 else "未设置"
            logger.info(f"将使用API密钥: {masked_key}")
    
    def _create_directories(self) -> None:
        """创建必要的目录结构"""
        paths = [
            Path(self.project_path) / "DeepSeek" / "Prompts",
            Path(self.project_path) / "DeepSeek" / "Responses",
            Path(self.project_path) / "DeepSeek" / "Reports"
        ]
        
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"确保目录存在: {path}")
    
    def get_optimization_suggestions(
        self, 
        simulation_results: Dict[str, Any], 
        iteration: int, 
        current_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成优化建议
        
        Args:
            simulation_results: 仿真结果字典
            iteration: 当前迭代次数
            current_parameters: 当前参数设置
            
        Returns:
            优化后的参数字典
        """
        logger.info(f"生成第{iteration}轮优化建议")
        
        # 生成提示
        prompt = self._generate_prompt_for_optimization(
            current_parameters=current_parameters,
            simulation_results=simulation_results,
            iteration=iteration
        )
        
        # 保存提示到文件
        prompt_file = Path(self.project_path) / "DeepSeek" / "Prompts" / f"prompt_iteration_{iteration}.md"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        logger.info(f"保存提示到文件: {prompt_file}")
        
        # 调用API
        response = self._call_api(prompt, iteration)
        
        # 保存响应到文件
        response_file = Path(self.project_path) / "DeepSeek" / "Responses" / f"response_iteration_{iteration}.md"
        with open(response_file, 'w', encoding='utf-8') as f:
            f.write(response)
        
        logger.info(f"保存响应到文件: {response_file}")
        
        # 解析响应
        optimized_parameters = self._parse_markdown_response(response, current_parameters)
        
        return optimized_parameters
    
    def _generate_prompt_for_optimization(
        self, 
        current_parameters: Dict[str, Any], 
        simulation_results: Dict[str, Any],
        iteration: int
    ) -> str:
        """
        为优化生成提示
        
        Args:
            current_parameters: 当前参数设置
            simulation_results: 仿真结果
            iteration: 当前迭代次数
            
        Returns:
            格式化的提示字符串
        """
        # 格式化参数
        formatted_parameters = "\n".join([f"- {key}: {value}" for key, value in current_parameters.items()])
        
        # 格式化结果
        formatted_results = "\n".join([f"- {key}: {value}" for key, value in simulation_results.items()])
        
        # 构建提示
        prompt = f"""# TCAD参数优化 - 第{iteration}轮

## 当前参数
{formatted_parameters}

## 仿真结果
{formatted_results}

## 任务
分析上述参数和仿真结果，基于你的TCAD和半导体器件专业知识，提出下一轮仿真的参数优化建议。目标是提高器件的耐受电压（latch_voltage），同时降低能量消耗（energy_consumption）和电荷收集（charge_collection）。

## 优化要求
1. 为每个参数提供一个新的推荐值
2. 必须为所有原始参数提供新值
3. 参数变化应当在原值的±30%范围内
4. 请解释每个参数变化的理由

## 输出格式
请使用以下Markdown格式回复：

```
# 优化建议

## 参数调整
| 参数 | 当前值 | 建议值 | 变化百分比 | 理由 |
|------|--------|--------|------------|------|
| Wtot | 值 | 值 | 百分比 | 简短理由 |
| ... | ... | ... | ... | ... |

## 预期结果
描述调整后预期的改进效果

## 优化参数
Wtot: 值
Wg: 值
Tdrift: 值
Ndrift: 值
Nwell: 值
Nsub: 值
Tox: 值
Tpoly: 值
Tcathode: 值
```

重要提示：请确保在"优化参数"部分包含所有原始参数，格式为"参数名: 值"，每行一个参数。这是必须的输出格式。
"""
        return prompt
    
    def _call_api(self, prompt: str, iteration: int) -> str:
        """
        调用DeepSeek API
        
        Args:
            prompt: 提示内容
            iteration: 当前迭代次数
            
        Returns:
            API响应文本
        """
        if self.use_simulation or not self.api_key:
            logger.warning("使用模拟响应模式 - 未调用实际API")
            return self._generate_simulated_response(prompt, iteration)
        
        # API端点
        api_url = "https://api.deepseek.com/v1/chat/completions"
        
        # API请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 准备消息
        messages = [
            {
                "role": "system",
                "content": "你是一个TCAD仿真专家，擅长优化半导体器件参数。请按照要求的格式提供参数优化建议。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # 准备请求数据
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "stream": False
        }
        
        # 打印详细信息
        if self.verbose:
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if self.api_key and len(self.api_key) > 8 else "未设置"
            logger.info(f"调用API - URL: {api_url}")
            logger.info(f"使用API密钥: {masked_key}")
            logger.info(f"请求模型: {self.model}")
            logger.info(f"消息数: {len(messages)}")
            logger.info(f"系统消息: {messages[0]['content'][:50]}...")
            logger.info(f"用户消息: {messages[1]['content'][:50]}...")
        
        # 调用API并处理重试
        for attempt in range(self.max_retries):
            try:
                logger.info(f"API调用尝试 {attempt + 1}/{self.max_retries}")
                
                # 发送请求
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
                
                # 检查响应状态
                if response.status_code == 200:
                    # 处理成功响应
                    result = response.json()
                    if self.verbose:
                        logger.info(f"API响应成功 - 状态码: {response.status_code}")
                    
                    # 提取内容
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if content:
                        return content
                    else:
                        logger.warning("API响应成功但内容为空")
                else:
                    # 处理错误响应
                    logger.error(f"API调用失败 - 状态码: {response.status_code}")
                    logger.error(f"错误详情: {response.text}")
            
            except Exception as e:
                logger.error(f"API调用异常: {str(e)}")
            
            # 重试前等待
            wait_time = 2 ** attempt  # 指数退避
            logger.info(f"等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
        
        # 如果所有尝试都失败，返回模拟响应
        logger.warning("所有API调用尝试均失败，使用模拟响应")
        return self._generate_simulated_response(prompt, iteration)
    
    def _generate_simulated_response(self, prompt: str, iteration: int) -> str:
        """
        生成模拟的API响应（用于测试和调试）
        
        Args:
            prompt: 提示内容
            iteration: 当前迭代次数
            
        Returns:
            模拟的响应文本
        """
        logger.info("生成模拟响应")
        
        # 从提示中提取当前参数
        current_params = {}
        param_section = False
        
        for line in prompt.split('\n'):
            if "## 当前参数" in line:
                param_section = True
                continue
            elif param_section and line.strip() == "":
                param_section = False
                continue
            
            if param_section and ": " in line:
                parts = line.strip("- ").split(": ")
                if len(parts) == 2:
                    param_name, param_value = parts
                    try:
                        current_params[param_name] = float(param_value)
                    except ValueError:
                        # 处理非数值参数
                        current_params[param_name] = param_value
        
        # 生成随机变化的参数
        optimized_params = {}
        param_changes = {}
        
        for name, value in current_params.items():
            if isinstance(value, (int, float)):
                # 生成-15%到+15%的随机变化
                change_percent = random.uniform(-0.15, 0.15)
                new_value = value * (1 + change_percent)
                
                # 记录变化
                optimized_params[name] = new_value
                param_changes[name] = {
                    "current": value,
                    "new": new_value,
                    "percent": change_percent * 100,
                    "reason": self._get_random_reason(name, change_percent)
                }
        
        # 构建模拟响应
        table_rows = []
        for name, change in param_changes.items():
            row = f"| {name} | {change['current']:.2f} | {change['new']:.2f} | {change['percent']:.2f}% | {change['reason']} |"
            table_rows.append(row)
        
        table_content = "\n".join(table_rows)
        
        params_text = "\n".join([f"{name}: {value}" for name, value in optimized_params.items()])
        
        response = f"""# 优化建议

## 参数调整
| 参数 | 当前值 | 建议值 | 变化百分比 | 理由 |
|------|--------|--------|------------|------|
{table_content}

## 预期结果
根据参数调整，预期器件的耐受电压会提高约{random.uniform(5, 15):.2f}%，同时能量消耗降低约{random.uniform(3, 10):.2f}%，电荷收集减少约{random.uniform(5, 12):.2f}%。

## 优化参数
{params_text}
"""
        return response
    
    def _get_random_reason(self, param_name: str, change_percent: float) -> str:
        """
        生成参数变化的随机理由
        
        Args:
            param_name: 参数名称
            change_percent: 变化百分比
            
        Returns:
            变化理由
        """
        # 参数特定理由库
        reasons = {
            "Wtot": [
                "增加总宽度以提高器件面积，降低电流密度",
                "减小总宽度以降低占用面积，减少寄生电容",
                "优化总宽度以平衡面积和性能"
            ],
            "Wg": [
                "增加栅极宽度以提高控制能力",
                "减小栅极宽度以降低寄生电容",
                "优化栅极宽度以改善沟道控制"
            ],
            "Tdrift": [
                "增加漂移区厚度以提高耐压能力",
                "减小漂移区厚度以降低导通电阻",
                "优化漂移区厚度以平衡耐压和导通电阻"
            ],
            "Ndrift": [
                "增加漂移区掺杂以降低导通电阻",
                "减小漂移区掺杂以提高击穿电压",
                "优化漂移区掺杂以平衡性能"
            ],
            "Nwell": [
                "增加N阱掺杂以降低电阻",
                "减小N阱掺杂以提高耐压",
                "优化N阱掺杂以减少热载流子效应"
            ],
            "Nsub": [
                "增加衬底掺杂以抑制闩锁效应",
                "减小衬底掺杂以降低寄生电容",
                "优化衬底掺杂以改善电场分布"
            ],
            "Tox": [
                "增加氧化层厚度以降低栅极电容",
                "减小氧化层厚度以提高栅极控制能力",
                "优化氧化层厚度以平衡栅极控制和栅极电容"
            ],
            "Tpoly": [
                "增加多晶硅厚度以降低栅极电阻",
                "减小多晶硅厚度以降低制造复杂度",
                "优化多晶硅厚度以改善栅极性能"
            ],
            "Tcathode": [
                "增加阴极厚度以提高电流能力",
                "减小阴极厚度以降低导通电阻",
                "优化阴极厚度以改善电流分布"
            ]
        }
        
        # 默认理由
        default_reasons = [
            "优化参数以提高整体性能",
            "调整参数以平衡耐压和损耗",
            "微调参数以改善器件特性"
        ]
        
        # 获取参数特定理由或默认理由
        param_reasons = reasons.get(param_name, default_reasons)
        
        # 根据变化方向选择合适的理由
        if change_percent > 0:
            # 对于增加的参数，选择第一个理由
            return param_reasons[0]
        elif change_percent < 0:
            # 对于减小的参数，选择第二个理由
            return param_reasons[1]
        else:
            # 对于不变的参数，选择第三个理由
            return param_reasons[2]
    
    def _parse_markdown_response(self, response: str, current_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析Markdown格式的响应，提取优化参数
        
        Args:
            response: API响应文本
            current_parameters: 当前参数值，作为备用
            
        Returns:
            解析后的参数字典
        """
        logger.info("解析Markdown响应")
        
        # 尝试使用正则表达式从"优化参数"部分提取参数
        optimized_params = {}
        
        # 提取"优化参数"部分
        optimization_section_match = re.search(r'## 优化参数\n(.*?)(?=\n#|$)', response, re.DOTALL)
        
        if optimization_section_match:
            optimization_section = optimization_section_match.group(1).strip()
            
            # 从优化参数部分逐行提取参数
            for line in optimization_section.split('\n'):
                if ':' in line:
                    parts = line.split(':', 1)
                    param_name = parts[0].strip()
                    param_value_str = parts[1].strip()
                    
                    try:
                        # 尝试转换为浮点数
                        param_value = float(param_value_str)
                        optimized_params[param_name] = param_value
                    except ValueError:
                        logger.warning(f"无法解析参数值: {line}")
        else:
            logger.warning("未找到优化参数部分，尝试从表格中提取")
            
            # 尝试从表格中提取参数
            table_pattern = r'\|\s*(\w+)\s*\|\s*[\d\.]+\s*\|\s*([\d\.]+)\s*\|'
            table_matches = re.findall(table_pattern, response)
            
            for param_name, param_value_str in table_matches:
                try:
                    param_value = float(param_value_str)
                    optimized_params[param_name] = param_value
                except ValueError:
                    logger.warning(f"无法从表格解析参数值: {param_name}: {param_value_str}")
        
        # 验证所有必需的参数是否都有
        for param_name in current_parameters.keys():
            if param_name not in optimized_params:
                logger.warning(f"优化响应中缺少参数: {param_name}，使用当前值")
                optimized_params[param_name] = current_parameters[param_name]
        
        logger.info(f"解析到 {len(optimized_params)} 个参数")
        if self.verbose:
            for name, value in optimized_params.items():
                logger.info(f"参数 {name}: {value}")
        
        return optimized_params
    
    def analyze_simulation_results(
        self,
        all_results: List[Dict[str, Any]],
        all_parameters: List[Dict[str, Any]]
    ) -> str:
        """
        分析仿真结果，生成总结报告
        
        Args:
            all_results: 所有迭代的仿真结果列表
            all_parameters: 所有迭代的参数列表
            
        Returns:
            分析报告（Markdown格式）
        """
        if not all_results or not all_parameters or len(all_results) != len(all_parameters):
            return "无法生成分析报告：数据不完整或不匹配"
        
        iterations = len(all_results)
        
        # 创建结果表格
        results_rows = []
        header = "| 迭代 | 闩锁电压 | 峰值电流 | 电荷收集 | 能量消耗 |"
        divider = "|------|----------|----------|----------|----------|"
        
        results_rows.append(header)
        results_rows.append(divider)
        
        for i, result in enumerate(all_results):
            iteration = i + 1
            row = f"| {iteration} | {result.get('latch_voltage', 'N/A'):.2f} | {result.get('peak_current', 'N/A'):.2f} | {result.get('charge_collection', 'N/A'):.2f} | {result.get('energy_consumption', 'N/A'):.2f} |"
            results_rows.append(row)
        
        results_table = "\n".join(results_rows)
        
        # 创建参数变化表格
        param_names = list(all_parameters[0].keys())
        
        params_rows = []
        params_header = "| 迭代 | " + " | ".join(param_names) + " |"
        params_divider = "|------|" + "|".join(["-" * 10 for _ in param_names]) + "|"
        
        params_rows.append(params_header)
        params_rows.append(params_divider)
        
        for i, params in enumerate(all_parameters):
            iteration = i + 1
            values = [f"{params.get(name, 'N/A'):.2f}" for name in param_names]
            row = f"| {iteration} | " + " | ".join(values) + " |"
            params_rows.append(row)
        
        params_table = "\n".join(params_rows)
        
        # 找到最佳结果
        best_iteration = None
        best_voltage = 0
        best_energy = float('inf')
        
        for i, result in enumerate(all_results):
            voltage = result.get('latch_voltage', 0)
            energy = result.get('energy_consumption', float('inf'))
            
            # 简单的多目标优化：首先看耐压，然后看能耗
            if voltage > best_voltage or (voltage == best_voltage and energy < best_energy):
                best_iteration = i + 1
                best_voltage = voltage
                best_energy = energy
        
        # 生成趋势分析
        latch_voltages = [result.get('latch_voltage', 0) for result in all_results]
        energy_consumptions = [result.get('energy_consumption', 0) for result in all_results]
        
        voltage_trend = "上升" if latch_voltages[-1] > latch_voltages[0] else "下降"
        energy_trend = "下降" if energy_consumptions[-1] < energy_consumptions[0] else "上升"
        
        voltage_change = ((latch_voltages[-1] - latch_voltages[0]) / latch_voltages[0]) * 100 if latch_voltages[0] != 0 else 0
        energy_change = ((energy_consumptions[-1] - energy_consumptions[0]) / energy_consumptions[0]) * 100 if energy_consumptions[0] != 0 else 0
        
        # 构建完整报告
        report = f"""# 仿真结果分析报告

## 总体概述
- 总迭代次数: {iterations}
- 最佳结果迭代: {best_iteration if best_iteration is not None else '无'}
- 最高闩锁电压: {best_voltage:.2f} V
- 对应能量消耗: {best_energy:.2f} μJ

## 趋势分析
- 闩锁电压趋势: {voltage_trend} ({voltage_change:.2f}%)
- 能量消耗趋势: {energy_trend} ({energy_change:.2f}%)

## 每轮仿真结果
{results_table}

## 参数变化
{params_table}

## 结论与建议
"""
        
        # 添加结论和建议
        if best_iteration is not None:
            best_params = all_parameters[best_iteration - 1]
            param_strings = [f"{name}: {value:.2f}" for name, value in best_params.items()]
            param_text = "\n".join(param_strings)
            
            report += f"""根据仿真结果分析，第{best_iteration}轮迭代获得了最佳性能，其闩锁电压为{best_voltage:.2f}V，能量消耗为{best_energy:.2f}μJ。建议采用以下参数设置：

```
{param_text}
```

进一步优化可考虑以下方向：
1. 继续调整{param_names[0]}和{param_names[1]}参数，可能获得更高的闩锁电压
2. 优化{param_names[2]}和{param_names[3]}参数，以降低能量消耗
3. 考虑更多迭代以探索更广泛的参数空间
"""
        else:
            report += """未能确定明确的最佳结果。建议：
1. 增加迭代次数以更充分地探索参数空间
2. 调整优化目标，可能当前的多目标优化存在冲突
3. 扩大参数变化范围，以寻找更优的解
"""
        
        # 保存报告到文件
        report_file = Path(self.project_path) / "DeepSeek" / "Reports" / "analysis_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"分析报告已保存至: {report_file}")
        
        return report 