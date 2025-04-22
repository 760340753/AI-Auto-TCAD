#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek交互模块，用于与DeepSeek AI模型交互获取优化建议
"""

import os
import json
import time
import logging
import requests
from pathlib import Path
from typing import Dict, Any, List, Union, Optional
import random
import numpy as np
import traceback
import re

from .parameter_manager import ParameterManager
from .utils import simulate_response

logger = logging.getLogger("auto_sim.deepseek_interaction")

class DeepSeekInteraction:
    """
    负责与DeepSeek AI服务交互的类
    """
    def __init__(self, api_key=None, simulation_mode=True):
        """
        初始化DeepSeek交互类

        Args:
            api_key: API密钥 (Silicon Flow)
            simulation_mode: 是否在模拟模式下运行
        """
        # 初始化日志记录器
        self.logger = logging.getLogger("auto_sim.deepseek_interaction")
        
        self.api_key = api_key
        self.simulation_mode = simulation_mode
        
        # 设置API URL和固定的模型名称
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        # 始终使用指定的 Pro 模型
        self.model_name = "Pro/deepseek-ai/DeepSeek-R1" 
        self.logger.info(f"将始终使用模型: {self.model_name}")
        
        # 设置提示和响应保存目录
        self.prompts_dir = "./DeepSeek/Prompts"
        self.responses_dir = "./DeepSeek/Responses"
        
        # 确保目录存在
        os.makedirs(self.prompts_dir, exist_ok=True)
        os.makedirs(self.responses_dir, exist_ok=True)

    def _call_api(self, messages: List[Dict[str, str]], 
                 model_name: str = None,
                 temperature: float = 0.7,
                 max_tokens: int = 2000,
                 response_format: Dict[str, str] = None) -> Dict[str, Any]:
        """
        调用DeepSeek API或生成模拟响应
        
        Args:
            messages: 消息列表，包含系统提示和用户查询
            model_name: 模型名称，默认为self.model_name
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成令牌数
            response_format: 响应格式，如{"type": "json_object"}或{"type": "text"}
            
        Returns:
            响应字典
        """
        # 如果没有指定模型名称，使用类中定义的固定模型
        if model_name is None:
            model_name = self.model_name
            
        # 如果没有指定响应格式，根据固定模型设置 (Pro 模型通常需要 text)
        if response_format is None:
             response_format = {"type": "text"}
        
        # 打印调试信息
        print(f"使用模型: {model_name}")
        print(f"响应格式: {response_format}")
        
        # 检查是否提供了API密钥
        if not self.api_key or self.simulation_mode:
            if not self.simulation_mode:
                print(f"警告: 未提供API密钥或处于模拟模式，将使用模拟响应")
            return self._generate_simulated_response(messages)
        
        # 打印API密钥部分内容（安全考虑）
        print(f"使用API密钥: {self.api_key[:5]}...{self.api_key[-5:]}")
        
        # 构建请求数据
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # 添加响应格式参数（如果有）
        if response_format:
            data["response_format"] = response_format
        
        # 打印请求信息
        print(f"API URL: {self.api_url}")
        print(f"请求头: {headers}")
        print(f"发送消息数: {len(messages)}")
        print(f"系统消息预览: {messages[0]['content'][:100]}...")
        print(f"用户消息预览: {messages[1]['content'][:100]}...")
        
        try:
            print("发送API请求...")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=120  # 增加超时时间到120秒
            )
            
            print(f"API响应状态码: {response.status_code}")
            print(f"API响应头: {response.headers}")
            
            if response.status_code == 200:
                response_data = response.json()
                content_length = len(str(response_data))
                print(f"API响应内容长度: {content_length}")
                print(f"API响应内容预览: {str(response_data)[:200]}...")
                return response_data
            else:
                print(f"API调用失败，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
                
                # 即使API调用失败，也返回模拟响应
                print("返回模拟响应...")
                return self._generate_simulated_response(messages)
                
        except Exception as e:
            print(f"调用API时发生异常: {str(e)}")
            print(f"异常堆栈: {traceback.format_exc()}")
            
            # 返回模拟响应
            print("返回模拟响应...")
            return self._generate_simulated_response(messages)

    def _generate_simulated_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """生成模拟的API响应"""
        print("生成模拟响应...")
        
        # 检查最后一条消息是否来自用户
        if not messages or messages[-1]["role"] != "user":
            return {"choices": [{"message": {"content": "错误: 没有用户消息"}}]}
        
        # 获取用户最后一条消息
        user_message = messages[-1]["content"]
        
        # 模拟一个基本响应
        if "请提供优化建议" in user_message:
            # 随机生成一些合理的参数调整
            content = self._generate_simulated_parameters()
        else:
            content = "我不确定如何回应你的请求。请提供更具体的信息，以便我生成参数建议。"
        
        # 构建响应格式
        response = {
            "id": f"chatcmpl-{random.randint(1000000, 9999999)}",
            "object": "chat.completion",
            "created": int(np.floor(np.datetime64('now').astype('float') / 1e9)),
            "model": "deepseek-chat",
            "usage": {
                "prompt_tokens": len(user_message),
                "completion_tokens": len(content),
                "total_tokens": len(user_message) + len(content)
            },
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop",
                    "index": 0
                }
            ]
        }
        
        return response

    def _generate_simulated_parameters(self) -> str:
        """
        生成模拟的参数建议，根据请求格式返回JSON或Markdown
        """
        params = {
            "Wtot": round(random.uniform(40, 60), 2),
            "Wg": round(random.uniform(8, 12), 2),
            "Tdrift": round(random.uniform(280, 320), 2),
            "Tox": round(random.uniform(0.08, 0.12), 3),
            "Tpoly": round(random.uniform(0.4, 0.6), 2),
            "Tcathode": round(random.uniform(0.8, 1.2), 2),
            "Tanode": round(random.uniform(0.8, 1.2), 2),
            "Nsubtop": f"{random.uniform(0.8, 1.2)}e+15",
            "Nsubbot": f"{random.uniform(0.8, 1.2)}e+19",
            "Ndrift": f"{random.uniform(0.8, 1.2)}e+14",
            "Npbase": f"{random.uniform(4, 6)}e+16",
            "Nbody": f"{random.uniform(0.8, 1.2)}e+17"
        }
        
        # 返回Markdown格式
        markdown = """## 参数优化建议

基于当前的模拟结果，我提出以下参数调整建议：

### 建议参数

| 参数 | 建议值 |
|------|-------|
"""
        
        for key, value in params.items():
            markdown += f"| {key} | {value} |\n"
        
        markdown += """
### 优化理由

1. 调整了Wtot和Wg参数以优化器件几何结构，这有助于提高latch电压。
2. 微调了Tdrift以在维持高latch电压的同时降低能量消耗。
3. 调整了掺杂浓度参数以优化电荷分布，减少能量消耗。

这些调整应该能够保持高latch电压（>500V）的同时降低能量消耗，并将电荷收集保持在合理范围内。
"""
        return markdown

    def _parse_markdown_response(self, markdown_response: str) -> Dict[str, float]:
        """
        解析Markdown格式的响应，提取参数名称和建议值
        
        Args:
            markdown_response: Markdown格式的响应文本
            
        Returns:
            包含参数名称和建议值的字典
        """
        self.logger.info("开始解析Markdown响应")
        parameters = {}
        table_found = False
        text_params_found = False
        
        # 检查响应是否包含JSON代码块
        json_pattern = r"```json(.*?)```"
        json_match = re.search(json_pattern, markdown_response, re.DOTALL)
        if json_match:
            try:
                json_text = json_match.group(1).strip()
                json_data = json.loads(json_text)
                
                # 提取参数
                for key, value in json_data.items():
                    if isinstance(value, (int, float)):
                        parameters[key] = float(value)
                        self.logger.info(f"从JSON提取参数: {key} = {value}")
                
                # 如果找到了参数，直接返回
                if parameters:
                    return parameters
            except json.JSONDecodeError:
                self.logger.warning("JSON解析失败")
        
        # 1. 首先尝试查找带有"参数"和"建议值"标题的表格
        table_patterns = [
            r"\|\s*参数\s*\|\s*建议值\s*\|[\s\S]*?(?=\n\n|\Z)",  # 中文标题表格
            r"\|\s*[\w\s]+\s*\|\s*[\w\s\.]+\s*\|[\s\S]*?(?=\n\n|\Z)",  # 一般表格格式
            r"\|\s*[\u4e00-\u9fa5\w\s]+\s*\|\s*[\w\s\.e\+\-]+\s*\|[\s\S]*?(?=\n\n|\Z)"  # 中文参数名表格
        ]
        
        for pattern in table_patterns:
            table_match = re.search(pattern, markdown_response)
            if table_match:
                table_found = True
                self.logger.info(f"找到参数表格，使用模式: {pattern}")
                table_text = table_match.group(0)
                
                rows = re.findall(r"\|(.*?)\|(.*?)\|", table_text)
                header_row = True
                for row in rows:
                    if header_row:
                        header_row = False
                        continue  # 跳过表头行
                        
                    if len(row) >= 2 and "---" not in row[0]:
                        param = row[0].strip()
                        value_str = row[1].strip()
                        try:
                            # 处理科学计数法
                            if 'e' in value_str.lower() or 'E' in value_str:
                                # 尝试处理可能的科学计数法格式问题
                                value_str = value_str.replace(' ', '')  # 移除可能的空格
                                # 检查是否有特殊格式，如1.25 e+17
                                sci_match = re.search(r'([\d\.]+)\s*[eE]\s*([+\-]?\d+)', value_str)
                                if sci_match:
                                    mantissa = sci_match.group(1)
                                    exponent = sci_match.group(2)
                                    value_str = f"{mantissa}e{exponent}"
                                
                                value = float(value_str)
                                # 如果是掺杂参数，使用科学计数法形式存储
                                if param.lower().startswith('doping') or param.lower().startswith('n') or param.lower().startswith('p'):
                                    parameters[param] = value
                                    self.logger.info(f"从表格提取参数: {param} = {value:.2e}")
                                    continue
                            else:
                                value = float(value_str)
                            
                            param = self._normalize_param_name(param)
                            parameters[param] = value
                            self.logger.info(f"从表格提取参数: {param} = {value}")
                        except ValueError:
                            self.logger.warning(f"无法将值转换为浮点数: {value_str}")

        # 3-7. [保持原有的正则表达式提取逻辑]
        # 尝试从文本中提取参数，如果表格未找到足够的参数
        if not table_found or len(parameters) < 3:
            text_patterns = [
                # 列表项式的键值对: - Wtot: 50
                r"[-\*]\s+(\w+)\s*:\s*([\d\.e\+\-]+)",
                r"[-\*]\s+(\w+)\s*[为是等于:：]\s*([\d\.e\+\-]+)",
                
                # 等号分隔的参数: Wtot = 50
                r"(\w+)\s*=\s*([\d\.e\+\-]+)",
                r"(\w+)\s*:\s*([\d\.e\+\-]+)(?!\|)",
                r"(\w+)\s*[为是等于:：]\s*([\d\.e\+\-]+)",
                
                # 中文描述的参数调整表述
                r"将\s*(\w+)\s*[设调]置为\s*([\d\.e\+\-]+)",
                r"(\w+)\s*[参数值]?[应建议需]?[该调]\s*[整改变为至]\s*([\d\.e\+\-]+)",
                r"(\w+)\s*[应建议]?[该调整]\s*[为到至]\s*([\d\.e\+\-]+)",
                r"(\w+)\s*[可需][以要][设调整改][为至到成]\s*([\d\.e\+\-]+)",
                r"(\w+)\s*[:]?\s*[从由]\s*[\d\.e\+\-]+\s*[改调整变][为到至]\s*([\d\.e\+\-]+)",
                r"把\s*(\w+)\s*[设调]置为\s*([\d\.e\+\-]+)",
                r"(\w+)\s*[设调整改][为至到成]\s*([\d\.e\+\-]+)",
                
                # 新增: 中文参数名与数值的组合
                r"[\u4e00-\u9fa5\s]*?(\w+)[\u4e00-\u9fa5\s]*?[值为:：]\s*([\d\.e\+\-]+)",
                r"[\u4e00-\u9fa5\s]*?(\w+)[\u4e00-\u9fa5\s]*?[应该改调整变][为至到]\s*([\d\.e\+\-]+)",
                r"参数\s*(\w+)\s*[为:：应该调整为改为]\s*([\d\.e\+\-]+)",
                r"[建优化]议[将把]?\s*(\w+)\s*[设改调][为到至成为]\s*([\d\.e\+\-]+)",
                
                # 新增: 数值前有各种单位的情况 (微米、纳米等)
                r"(\w+)[\u4e00-\u9fa5\s]*?[为:：]\s*([\d\.]+)\s*[微纳皮]?米",
                r"(\w+)[\u4e00-\u9fa5\s]*?[为:：]\s*([\d\.]+)\s*[kKMmGgTt]?[vV]",
                
                # 新增: 科学计数法的特殊情况
                r"(\w+)[\u4e00-\u9fa5\s]*?[为:：]\s*([\d\.]+)\s*[×xX]\s*10[\^]?\s*([+\-]?\d+)",
                
                # 新增: 其他可能的格式
                r"(\w+)\s*参数[调改设][整为至到]\s*([\d\.e\+\-]+)",
                r"对[于参数]\s*(\w+)[，,]?\s*[我建]议[值为:：使用调整为]\s*([\d\.e\+\-]+)",
                
                # 增加更多模式来提高匹配率
                r"(\w+)\s*的值[\u4e00-\u9fa5\s]*?为\s*([\d\.e\+\-]+)",
                r"(\w+)\s*[\u4e00-\u9fa5\s]*?参数调整为\s*([\d\.e\+\-]+)",
                r"(\w+)\s*[\u4e00-\u9fa5\s]*?值为\s*([\d\.e\+\-]+)\s*[微纳皮]?米",
                r"(\w+)\s*的新值应为\s*([\d\.e\+\-]+)",
                r"(\w+)\s*应[当该]为\s*([\d\.e\+\-]+)",
                r"(\w+)\s*的最佳值[应是为]\s*([\d\.e\+\-]+)",
                r"建议\s*(\w+)\s*[：:=]\s*([\d\.e\+\-]+)",
                r"(\w+)\s*应调[整至为到]\s*([\d\.e\+\-]+)",
                r"(\w+)\s*[\u4e00-\u9fa5\s]*?减小到\s*([\d\.e\+\-]+)",
                r"(\w+)\s*[\u4e00-\u9fa5\s]*?增加到\s*([\d\.e\+\-]+)",
                r"(\w+)\s*参数[：:=为是]\s*([\d\.e\+\-]+)",
                
                # 带有标点符号和空格的模式
                r"[\"\'\(（](\w+)[\"\'\)）][\u4e00-\u9fa5\s]*?[：:=为是]\s*([\d\.e\+\-]+)",
                r"参数[\"\'\(（](\w+)[\"\'\)）][\u4e00-\u9fa5\s]*?[：:=为是]\s*([\d\.e\+\-]+)",
                r"(\w+)\s*[参数]?[：:=]\s*[\"\'\(（]([\d\.e\+\-]+)[\"\'\)）]",
                
                # 更复杂的科学计数法匹配
                r"(\w+)\s*[为是:：]\s*([\d\.]+)[eE]\s*([+\-]?\d+)",
                r"(\w+)\s*[为是:：]\s*([\d\.]+)\s*×\s*10\s*\^\s*([+\-]?\d+)",
                r"(\w+)\s*[为是:：]\s*([\d\.]+)\s*[xX]\s*10\s*\^\s*([+\-]?\d+)",
            ]
            
            for pattern in text_patterns:
                matches = re.findall(pattern, markdown_response)
                for match in matches:
                    try:
                        if len(match) == 2:
                            param, value_str = match
                            # 处理科学计数法
                            if 'e' in value_str.lower() or 'E' in value_str:
                                value_str = value_str.replace(' ', '')  # 移除可能的空格
                                sci_match = re.search(r'([\d\.]+)\s*[eE]\s*([+\-]?\d+)', value_str)
                                if sci_match:
                                    mantissa = sci_match.group(1)
                                    exponent = sci_match.group(2)
                                    value_str = f"{mantissa}e{exponent}"
                        elif len(match) == 3:  # 处理科学计数法格式 (如 1.25 × 10^17)
                            param, mantissa, exponent = match
                            value_str = f"{mantissa}e{exponent}"
                        else:
                            continue
                            
                        value = float(value_str)
                        param = self._normalize_param_name(param)
                        
                        # 判断是否是掺杂参数
                        if param.lower().startswith('doping') or param.lower().startswith('n') or param.lower().startswith('p'):
                            parameters[param] = value
                            self.logger.info(f"从文本提取参数(掺杂): {param} = {value:.2e}")
                        else:
                            parameters[param] = value
                            self.logger.info(f"从文本提取参数: {param} = {value}")
                            
                        text_params_found = True
                    except (ValueError, IndexError) as e:
                        self.logger.warning(f"提取参数时出错: {e}")
            
            # 中文特殊的表述方式
            special_patterns = [
                # 单独处理掺杂浓度的特殊格式
                r"掺杂(\d+)[的值浓度]*[为:：]\s*([\d\.]+)\s*[×xX]\s*10[\^]?\s*([+\-]?\d+)",
                r"[第]?(\d+)[层区域]?掺杂[浓度值]*[为:：]\s*([\d\.]+)\s*[×xX]\s*10[\^]?\s*([+\-]?\d+)",
                r"Doping(\d+)[的值浓度]*[为:：]\s*([\d\.]+)\s*[×xX]\s*10[\^]?\s*([+\-]?\d+)",
                r"[掺杂浓度参数]*[Nn](\d+)[的值浓度]*[为:：应该是]\s*([\d\.]+)\s*[×xX]\s*10[\^]?\s*([+\-]?\d+)",
                r"[掺杂浓度参数]*[Pp](\d+)[的值浓度]*[为:：应该是]\s*([\d\.]+)\s*[×xX]\s*10[\^]?\s*([+\-]?\d+)",
                
                # 新增掺杂浓度的其他表述方式
                r"掺杂(\d+)\s*[=为是:：]\s*([\d\.]+)\s*[eE]\s*([+\-]?\d+)",
                r"Doping(\d+)\s*[=为是:：]\s*([\d\.]+)\s*[eE]\s*([+\-]?\d+)",
                r"第(\d+)层掺杂[浓度值应为建议设为调整为改为]\s*([\d\.]+)\s*[eE]\s*([+\-]?\d+)",
                r"[Nn](\d+)\s*[=为是:：]\s*([\d\.]+)\s*[eE]\s*([+\-]?\d+)",
                r"[Pp](\d+)\s*[=为是:：]\s*([\d\.]+)\s*[eE]\s*([+\-]?\d+)",
                
                # 处理掺杂浓度的其他描述方式
                r"掺杂浓度(\d+)[为是:：]\s*([\d\.]+)\s*[×xX]\s*10[\^]?\s*([+\-]?\d+)",
                r"掺杂区域(\d+)[的值为是:：]\s*([\d\.]+)\s*[×xX]\s*10[\^]?\s*([+\-]?\d+)",
                r"第(\d+)个掺杂[参数值][为是:：]\s*([\d\.]+)\s*[×xX]\s*10[\^]?\s*([+\-]?\d+)",
                r"掺杂参数(\d+)[应为是:：]\s*([\d\.]+)\s*[×xX]\s*10[\^]?\s*([+\-]?\d+)",
            ]
            
            for pattern in special_patterns:
                matches = re.findall(pattern, markdown_response)
                for match in matches:
                    try:
                        if len(match) == 3:
                            index, mantissa, exponent = match
                            param = f"Doping{index}"
                            value = float(f"{mantissa}e{exponent}")
                            parameters[param] = value
                            self.logger.info(f"从特殊格式提取掺杂参数: {param} = {value:.2e}")
                            text_params_found = True
                    except (ValueError, IndexError) as e:
                        self.logger.warning(f"提取特殊格式参数时出错: {e}")
                
        if not table_found and not text_params_found:
            self.logger.warning("未找到任何参数表格或文本参数")
            
        # 后处理：强制转换需要科学计数法的参数
        self.logger.debug(f"解析后的原始参数: {parameters}")
        parameters = self._enforce_scientific_notation(parameters)
        self.logger.info(f"后处理强制科学计数法后的参数: {parameters}")
            
        return parameters
    
    def _enforce_scientific_notation(self, params: Dict[str, float]) -> Dict[str, float]:
        """检查参数字典，对特定参数强制使用科学计数法格式 (float 类型)"""
        # 定义需要强制使用科学计数法的参数名 (小写) 或判断条件
        scientific_params = ['na', 'nb', 'ndrift', 'pc', 'pb', 'pa', 'npoly', 'doping'] # 添加所有可能的掺杂参数前缀或全名
        magnitude_threshold_high = 1e6
        magnitude_threshold_low = 1e-4

        processed_params = {}
        for key, value in params.items():
            original_value = value # 保留原始值用于日志记录
            needs_conversion = False
            
            # 检查参数名是否需要科学计数法
            lower_key = key.lower()
            if any(lower_key.startswith(p) for p in scientific_params):
                needs_conversion = True
                self.logger.debug(f"参数 '{key}' 因名称匹配，检查科学计数法格式。")
            
            # 检查数值大小是否需要科学计数法 (仅对 float 类型)
            if isinstance(value, float) and not needs_conversion:
                if abs(value) >= magnitude_threshold_high or (value != 0 and abs(value) <= magnitude_threshold_low):
                    needs_conversion = True
                    self.logger.debug(f"参数 '{key}' 因数值大小 ({value})，检查科学计数法格式。")
            
            # 如果需要转换且当前不是科学计数法格式的 float (或者已经是科学计数法但想统一格式)
            if needs_conversion and isinstance(value, float):
                # 检查当前浮点数表示是否已经是标准的科学计数法字符串 (近似检查)
                # 或者直接重新格式化以确保统一
                formatted_value_str = f"{value:.2e}" # 格式化为科学计数法字符串
                try:
                    # 转换回 float 以存储。注意：存储的仍然是 float，只是格式化输出时会不同
                    # 如果下游需要特定字符串格式，这里可以直接存字符串
                    formatted_value_float = float(formatted_value_str)
                    if value != formatted_value_float: # 仅在格式化后数值不同时记录
                       self.logger.info(f"强制参数 '{key}' 的值 {original_value} 使用科学计数法 (存储为 float: {formatted_value_float})，格式化显示: {formatted_value_str}")
                    processed_params[key] = formatted_value_float
                except ValueError:
                     self.logger.warning(f"无法将格式化的科学计数法字符串 '{formatted_value_str}' 转回 float，保留原始值 {value}")
                     processed_params[key] = value # 保留原始值
            else:
                # 不需要转换或不是 float，保留原样
                processed_params[key] = value
                
        return processed_params
        
    def _extract_json_params(self, json_data, parameters):
        """
        从JSON数据中提取参数，支持嵌套结构
        
        Args:
            json_data: JSON数据
            parameters: 要填充的参数字典
        """
        # 如果是字典，遍历键值对
        if isinstance(json_data, dict):
            # 直接处理参数
            for key, value in json_data.items():
                # 如果键是parameters，直接提取
                if key == "parameters" and isinstance(value, dict):
                    for param, param_value in value.items():
                        if isinstance(param_value, (int, float)):
                            param = self._normalize_param_name(param)
                            parameters[param] = float(param_value)
                            self.logger.info(f"从JSON提取参数: {param} = {param_value}")
                # 如果值是数字，直接添加
                elif isinstance(value, (int, float)):
                    key = self._normalize_param_name(key)
                    parameters[key] = float(value)
                    self.logger.info(f"从JSON提取参数: {key} = {value}")
                # 如果值是字典，递归提取
                elif isinstance(value, dict):
                    self._extract_json_params(value, parameters)
                # 如果值是列表，遍历列表
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._extract_json_params(item, parameters)
        
    def _normalize_param_name(self, param_name: str) -> str:
        """
        规范化参数名，去除无关前缀和后缀
        
        Args:
            param_name: 原始参数名
            
        Returns:
            规范化后的参数名
        """
        # 移除常见的无关前缀和后缀
        prefixes_to_remove = [
            "的最佳", "最佳", "的建议", "建议", "的优化", "优化", 
            "以尝试设置", "目前可以设置", "但目前可", "目前可", "可以", 
            "可", "以", "但", "的"
        ]
        
        original = param_name
        for prefix in prefixes_to_remove:
            if param_name.startswith(prefix):
                param_name = param_name[len(prefix):]
            elif prefix in param_name:
                param_name = param_name.replace(prefix, "")
                
        # 如果参数名变化，记录日志
        if original != param_name:
            self.logger.debug(f"规范化参数名: {original} -> {param_name}")
            
        return param_name

    def get_optimization_suggestions(self, current_params, simulation_results, iteration_number):
        """
        基于当前参数和仿真结果获取优化建议
        
        Args:
            current_params: 当前参数字典
            simulation_results: 仿真结果字典
            iteration_number: 当前迭代次数
            
        Returns:
            dict: 优化后的参数字典
        """
        # 构建系统提示
        system_prompt = self._construct_system_prompt()
        
        # 构建用户查询
        user_query = self._construct_user_query(iteration_number, current_params, simulation_results)
        
        # 准备消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        # 保存提示
        prompt_file = os.path.join(self.prompts_dir, f"prompt_iteration_{iteration_number}.json")
        with open(prompt_file, "w") as f:
            json.dump(messages, f, indent=2)
        
        # 使用固定的模型和响应格式
        model_name = self.model_name
        response_format = {"type": "text"} # Pro 模型通常需要 text
        
        # 调用API
        response = self._call_api(
            messages=messages,
            model_name=model_name,
            temperature=0.7,
            max_tokens=2000,
            response_format=response_format
        )
        
        # 获取响应内容
        raw_response = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        
        # 保存响应
        response_file = os.path.join(self.responses_dir, f"response_iteration_{iteration_number}.json")
        with open(response_file, "w") as f:
            f.write(raw_response if isinstance(raw_response, str) else json.dumps(raw_response, indent=2))
        
        # 解析响应 (因为始终使用 Pro 模型，所以始终解析 Markdown)
        parsed_params = self._parse_markdown_response(raw_response) # 解析 Markdown

        # 返回解析后的参数和原始响应
        return parsed_params, raw_response
        
    def _construct_system_prompt(self) -> str:
        """构建系统提示 (针对 IGBT 项目)"""
        return """你是一位专业的沟槽栅 IGBT 器件 TCAD 模拟优化专家。你的任务是分析当前 TCAD 模拟参数和结果（特别是击穿电压 BV 和阈值电压 Vth），然后提供下一次迭代的优化参数建议。

请严格遵守以下要求：
1. 理解 IGBT 参数（如 Xmax, Wgate, Ygate, Ndrift, Pbase 等）对器件性能（击穿电压 BV、阈值电压 Vth、导通压降 Vce_sat 等）的影响。
2. **优化目标:** 提高击穿电压 (BV) 至 **1450V 以上**，同时确保阈值电压 (Vth) **低于 10V**。
3. 基于之前的模拟结果，提出合理的参数调整建议，以逼近优化目标。
4. **重要：**在提供参数建议之前，**必须先用一段话简要解释你做出这些调整建议的理由**，说明你认为调整哪些参数、为什么这样调整，以及期望达到什么效果。
5. 所有参数调整必须在物理和工艺允许的范围内。
6. **输出格式要求:**
    - 先输出解释理由的文本段落。
    - 然后输出**必须**是具体的参数值，不要提供范围或描述性建议。
    - **单位约定:** 长度参数 (Xmax, Wgate, Ypplus等) 单位为微米(μm)。电压参数 (BV, Vth, Vce_sat等) 单位为伏特(V)。掺杂浓度 (Ndrift, Pbase, Pplus等) 单位为每立方厘米(cm⁻³)。
    - **返回值要求:** 提供建议值时，**必须只返回纯数字**，**不得**包含任何单位符号（μm, V, cm⁻³ 等）。
    - **科学计数法:** 掺杂浓度参数**必须**使用科学计数法 (`数字e+指数`)。
7. **输出结构:** 以 Markdown 表格形式回复参数建议，并在末尾以 "优化参数" 标题列出所有需要更新的参数及其新建议值 (`参数名: 值`，每行一个)。

**再次强调:** 掺杂浓度参数**必须**使用科学计数法！所有返回值**不得**包含单位！

示例输出片段：

| 参数   | 建议值   |
| :----- | :------- |
| Ypbase | 3.2      |
| Ndrift | 4.8e+13  |
| Pbase  | 2.6e+17  |

优化参数
Xmax: 6.1
...
Ndrift: 4.8e+13
Pbase: 2.6e+17
...
Tox_sidewall: 0.11
"""

    def _construct_user_query(self, iteration_number, current_params, simulation_results):
        """构建发送给DeepSeek的用户查询 (针对 IGBT 项目)"""
        self.logger.info("构建 IGBT 用户查询...")
        
        # 构建参数部分
        params_text = "Current Parameters:\n"
        # 确保参数顺序或使用字典迭代
        for param_name, param_value in current_params.items():
            # 对掺杂浓度格式化为科学计数法显示给 LLM
            if "n" in param_name.lower() or "p" in param_name.lower() or "doping" in param_name.lower(): 
                 try:
                     params_text += f"{param_name}: {param_value:.2e}\n"
                 except (ValueError, TypeError):
                      params_text += f"{param_name}: {param_value}\n" # 无法格式化则原样输出
            else:
                 params_text += f"{param_name}: {param_value}\n"
            
        # 构建结果部分 - 重点突出 BV 和 Vth
        results_text = "Simulation Results:\n"
        breakdown_voltage = simulation_results.get('breakdown_voltage', 'N/A')
        threshold_voltage = simulation_results.get('threshold_voltage', 'N/A')
        results_text += f"Breakdown Voltage (BV): {breakdown_voltage} V\n"
        results_text += f"Threshold Voltage (Vth): {threshold_voltage} V\n"
        # 添加其他可能相关的结果
        for result_name, result_value in simulation_results.items():
             if result_name not in ['breakdown_voltage', 'threshold_voltage', 'parsed_node_id', 'parsed_tool_label']: # 避免重复和内部字段
                results_text += f"{result_name}: {result_value}\n"
            
        # 构建完整查询
        query = f"""I am performing iteration {iteration_number} of FS-IGBT device TCAD simulation optimization.

{params_text}

{results_text}

Optimization Goal: Increase Breakdown Voltage (BV) above 1450V while keeping Threshold Voltage (Vth) below 10V.

Please analyze the current parameters and results, then provide parameter adjustment suggestions for the next iteration to approach the goal.
Respond in Markdown table format with suggested values (numbers only, use scientific notation like 1.23e+14 for doping concentrations). 
List all parameters to be updated under the '优化参数' heading at the end.
Consider physical plausibility and make reasonable adjustments.
"""

        self.logger.info(f"User query constructed:\n{query[:500]}...") # Log preview
        return query

    def run_simulation_cycle(self, current_params, simulation_results, iteration_number):
        """运行单次仿真循环，调用API获取优化建议并返回新参数
        
        Args:
            current_params: 当前的参数字典
            simulation_results: 当前的仿真结果字典
            iteration_number: 当前迭代次数
            
        Returns:
            Dict[str, Any]: 优化后的参数字典
        """
        logger.info(f"开始第{iteration_number}轮仿真循环...")
        
        try:
            # 调用DeepSeek API获取优化建议
            optimized_params, raw_response = self.get_optimization_suggestions(
                current_params=current_params,
                simulation_results=simulation_results,
                iteration_number=iteration_number
            )
            
            logger.info(f"优化建议已获取: {optimized_params}")
            return optimized_params, raw_response
            
        except Exception as e:
            logger.error(f"仿真循环运行失败: {str(e)}")
            logger.error(traceback.format_exc())
            # 遇到错误时，返回原始参数
            return current_params, ""

    def get_intermediate_summary(self, iteration_data: List[Dict[str, Any]]) -> str:
        """
        调用 DeepSeek API 生成基于最近几次迭代的总结报告 (Markdown)。
        
        Args:
            iteration_data: 包含最近几次迭代信息的列表，
                            每个元素是包含 'iteration', 'params', 'results', 'optimized_params' 的字典。
                            
        Returns:
            str: DeepSeek 生成的 Markdown 格式总结报告内容，如果失败则返回空字符串。
        """
        if not iteration_data:
            self.logger.warning("没有提供迭代数据，无法生成中间总结。")
            return ""
            
        start_iter = iteration_data[0]['iteration']
        end_iter = iteration_data[-1]['iteration']
        self.logger.info(f"请求 DeepSeek 生成第 {start_iter}-{end_iter} 轮的中间总结...")
        
        # 构建系统提示
        system_prompt = """你是一个专业的半导体器件TCAD模拟优化分析师。
你的任务是分析给定的一系列仿真迭代数据（参数、结果），并生成一份简洁的 Markdown 格式总结报告。

报告应包含以下内容：
1.  **总体趋势分析:** 基于提供的仿真结果数据，描述关键性能指标的变化趋势。
2.  **关键参数变化:** 指出与性能变化关联最显著的参数调整是哪些。
3.  **进展评估:** 评估当前优化方向是否有效，是否在接近（如果有定义的）优化目标？
4.  **后续建议 (可选):** 基于趋势，可以简要提出对接下来的优化方向的看法。

请确保输出是结构清晰的 Markdown 格式，使用标题、列表等元素。重点分析**实际存在于输入数据中**的指标。不要包含任何 JSON 或代码块。
"""
        
        # 构建用户查询
        # 先构建固定部分
        user_query_header = f"# 仿真迭代数据 ({start_iter}-{end_iter}轮)\n\n请根据以下数据生成一份总结报告：\n\n"
        user_query_body = ""
        
        for entry in iteration_data:
            iter_num = entry['iteration']
            params = entry['params']
            results = entry['results']
            suggestions = entry.get('optimized_params', {}) # 获取该轮产生的建议
            
            # 使用三引号 f-string 处理多行内容
            user_query_body += f"""## Iteration {iter_num}

**Input Parameters:**
```json
{json.dumps(params, indent=2)}
```

**Simulation Results:**
```json
{json.dumps(results, indent=2)}
```

""" # 结束三引号 f-string
            # if suggestions:
            #     user_query_body += f"**AI Suggestion (for next iter):**
            #     ```json
            #     {json.dumps(suggestions, indent=2)}
            #     ```
            #     
            #     """
            user_query_body += "---\n"

        # 添加结尾
        user_query_footer = "\n请生成 Markdown 总结报告。"
        
        # 拼接完整的 user_query
        user_query = user_query_header + user_query_body + user_query_footer

        # 准备消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        # 保存提示
        prompt_file = os.path.join(self.prompts_dir, f"prompt_summary_{start_iter}-{end_iter}.json")
        with open(prompt_file, "w") as f:
            json.dump(messages, f, indent=2)
            
        # 调用 API
        try:
            response = self._call_api(
                messages=messages,
                model_name=self.model_name, # 使用固定的模型
                temperature=0.5, # 总结任务可能需要较低的温度以保持一致性
                max_tokens=1500, # 为总结报告留出足够空间
                response_format={"type": "text"} # 要求纯文本/Markdown
            )
            
            # 获取响应内容
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 保存响应
            response_file = os.path.join(self.responses_dir, f"response_summary_{start_iter}-{end_iter}.md")
            with open(response_file, "w", encoding='utf-8') as f:
                f.write(content)
                
            self.logger.info(f"DeepSeek 已生成中间总结报告内容 ({start_iter}-{end_iter})。")
            return content
            
        except Exception as e:
            self.logger.error(f"调用 DeepSeek 生成中间总结报告时出错: {e}")
            self.logger.error(traceback.format_exc())
            return ""