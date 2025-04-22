#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API封装，通过siliconflow.cn调用DeepSeek模型
简化版API调用模块，只实现核心功能
"""

import os
import json
import time
import logging
from pathlib import Path
from openai import OpenAI

logger = logging.getLogger("auto_sim.deepseek_api")

class DeepSeekAPI:
    """DeepSeek API封装，使用OpenAI库通过siliconflow调用DeepSeek模型"""
    
    def __init__(self, project_path, api_key=None, use_simulation=False):
        """
        初始化DeepSeek API
        
        Args:
            project_path (str): 项目路径，用于保存交互记录
            api_key (str, optional): DeepSeek API密钥
            use_simulation (bool, optional): 是否使用模拟模式，默认为False
        """
        self.project_path = Path(project_path)
        self.api_key = api_key
        self.use_simulation = use_simulation
        
        # 创建DeepSeek文件夹结构
        self.deepseek_dir = self.project_path / "DeepSeek"
        self.prompts_dir = self.deepseek_dir / "Prompts"
        self.responses_dir = self.deepseek_dir / "Responses"
        self.condensed_dir = self.deepseek_dir / "Condensed"
        
        self.deepseek_dir.mkdir(exist_ok=True)
        self.prompts_dir.mkdir(exist_ok=True)
        self.responses_dir.mkdir(exist_ok=True)
        self.condensed_dir.mkdir(exist_ok=True)
        
        logger.info(f"初始化DeepSeekAPI，项目路径: {project_path}，是否使用模拟: {use_simulation}")
        
        # 初始化OpenAI客户端
        if not use_simulation and api_key:
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.siliconflow.cn/v1"
                )
                logger.info("已初始化OpenAI客户端，使用siliconflow API")
            except Exception as e:
                logger.error(f"初始化OpenAI客户端失败: {str(e)}")
                self.client = None
                self.use_simulation = True
        else:
            self.client = None
            if not api_key:
                logger.warning("未提供API密钥，将使用模拟模式")
                self.use_simulation = True
    
    def _call_api(self, messages):
        """
        调用DeepSeek API
        
        Args:
            messages (list): 消息列表
            
        Returns:
            str: API响应
        """
        if self.use_simulation or not self.client:
            logger.info("使用模拟模式")
            return self._get_simulated_response(messages)
        
        try:
            logger.info("调用siliconflow DeepSeek API")
            response = self.client.chat.completions.create(
                model="Pro/deepseek-ai/DeepSeek-R1",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            content = response.choices[0].message.content
            logger.info(f"API调用成功，响应长度: {len(content)}")
            return content
        except Exception as e:
            logger.error(f"API调用失败: {str(e)}")
            logger.warning("使用模拟模式作为后备")
            return self._get_simulated_response(messages)
    
    def _get_simulated_response(self, messages):
        """
        获取模拟响应
        
        Args:
            messages (list): 消息列表
            
        Returns:
            str: 模拟响应
        """
        # 提取最后一条用户消息
        user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        
        # 生成模拟响应
        if "优化" in user_message and "参数" in user_message:
            content = """根据当前仿真结果和参数设置，我建议以下优化：

1. 调整Wtot参数：
   从当前的{:.2f}增加到{:.2f}，这将提高器件的耐压能力。

2. 减小Wg参数：
   从{:.2f}减小到{:.2f}，可以降低通道电阻并减少单粒子效应敏感区域。

3. 提高Ndrift掺杂浓度：
   从{:.2e}提高到{:.2e}，这有助于形成更强的电场降低电荷收集。

这些调整综合考虑了击穿电压、电荷收集效率和能量消耗等指标，应该能够显著改善器件性能。""".format(
                50, 55,         # Wtot: 当前值, 建议值
                10, 8.5,        # Wg: 当前值, 建议值
                5e13, 7.5e13    # Ndrift: 当前值, 建议值
            )
        else:
            content = """分析当前仿真结果表明，该器件结构在单粒子效应下表现一般。主要存在以下问题：

1. 电荷收集效率过高，表明器件对辐射粒子过于敏感
2. 闩锁电压较低，可能导致器件在实际应用中容易受到辐射损伤
3. 能量消耗偏高，这可能影响器件的长期可靠性

建议在下一轮仿真中尝试优化以下方面：
- 调整掺杂分布，特别是漂移区的掺杂梯度
- 修改几何尺寸，尤其是敏感区域的尺寸和形状
- 考虑引入额外的保护结构，如guard ring等"""
        
        # 构建符合OpenAI响应格式的字典
        response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "deepseek-chat",
            "usage": {
                "prompt_tokens": len(str(messages)),
                "completion_tokens": len(content),
                "total_tokens": len(str(messages)) + len(content)
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
    
    def get_optimization_suggestions(self, iteration, params, simulation_results, sde_code=None, sdevice_code=None, condensed_experience=None):
        """
        获取DeepSeek AI的优化建议
        
        Args:
            iteration: 当前迭代次数
            params: 当前参数
            simulation_results: 仿真结果
            sde_code: SDE代码（可选）
            sdevice_code: SDevice代码（可选）
            condensed_experience: 浓缩的历史经验（可选）
            
        Returns:
            dict: 优化后的参数
        """
        if self.use_simulation:
            logger.info(f"生成第 {iteration} 次迭代的假优化建议")
            # 构建系统提示
            system_prompt = """你是一位经验丰富的半导体器件TCAD模拟专家。你的任务是分析当前的TCAD仿真参数和结果，并提供改进的参数建议。"""
            
            # 格式化参数和结果
            params_formatted = "\n".join([f"- {key}: {value}" for key, value in params.items()])
            results_formatted = "\n".join([f"- {key}: {value}" for key, value in simulation_results.items()])
            
            # 构建用户消息
            user_prompt = f"""# 当前迭代信息
迭代次数: {iteration}

## 当前参数
{params_formatted}

## 仿真结果
{results_formatted}

## 请提供优化建议
请分析以上参数和结果，提供改进的参数建议。"""
            
            # 构建消息列表
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 调用模拟响应方法
            response = self._get_simulated_response(messages)
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            
            # 解析模拟响应
            return self._parse_suggestions(content, params)
        
        # 构建系统提示
        system_prompt = """你是一位经验丰富的半导体器件TCAD模拟专家。你的任务是分析当前的TCAD仿真参数和结果，并提供改进的参数建议。

请基于提供的参数和仿真结果，给出详细而有针对性的参数优化建议。你的建议应该具有明确的物理理论依据，并解释每个参数变更的预期效果。
"""
        
        # 构建用户提示
        # 格式化参数和结果
        params_formatted = "\n".join([f"- {key}: {value}" for key, value in params.items()])
        results_formatted = "\n".join([f"- {key}: {value}" for key, value in simulation_results.items()])
        
        # 构建完整的提示
        user_prompt = f"""# 当前迭代信息
迭代次数: {iteration}

## 当前参数
{params_formatted}

## 仿真结果
{results_formatted}

## 性能目标
- 提高latch电压（VST）：目标值 > 700V
- 优化能量消耗和电荷收集
"""
        
        # 添加SDE和SDevice代码片段（如果有）
        sde_part = ""
        if sde_code:
            sde_part = f"SDE代码片段:\n```\n{sde_code[:500]}...\n```\n"
            
        sdevice_part = ""
        if sdevice_code:
            sdevice_part = f"SDevice代码片段:\n```\n{sdevice_code[:500]}...\n```\n"
        
        # 添加历史经验（如果有）
        experience_part = ""
        if condensed_experience:
            experience_part = f"""
## 历史经验总结
{condensed_experience}
"""
            
        user_prompt += f"""
{sde_part}
{sdevice_part}
{experience_part}

请分析以上信息，提供以下内容：
1. 简要评估当前仿真结果的优劣
2. 详细的参数调整建议，包括具体的参数值
3. 每项调整的预期效果和理论依据
"""
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 保存提示
        prompt_file = self.prompts_dir / f"prompt_iteration_{iteration}.json"
        with open(prompt_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存提示到: {prompt_file}")
        
        # 调用API
        response = self._call_api(messages)
        
        # 保存响应
        response_file = self.responses_dir / f"response_iteration_{iteration}.json"
        with open(response_file, "w", encoding="utf-8") as f:
            json.dump(response, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存响应到: {response_file}")
        
        # 解析响应
        suggested_params = self._parse_suggestions(response, params)
        
        return suggested_params
    
    def _parse_suggestions(self, response_text, current_params):
        """
        从响应文本解析参数建议
        
        Args:
            response_text (str): 响应文本
            current_params (dict): 当前参数
            
        Returns:
            dict: 建议的参数
        """
        # 复制当前参数，用于返回建议
        suggested_params = current_params.copy()
        
        # 简单的解析逻辑
        import re
        
        # 尝试查找类似"将X从Y调整到Z"的模式
        pattern = r'([A-Za-z]+[A-Za-z0-9_]*)\s*(?:从|由)\s*([0-9.eE+-]+)\s*(?:到|调整到|改为|变为)\s*([0-9.eE+-]+)'
        matches = re.findall(pattern, response_text)
        
        for param_name, old_value, new_value in matches:
            if param_name in current_params:
                try:
                    # 转换值类型
                    current_value = current_params[param_name]
                    if isinstance(current_value, int):
                        suggested_params[param_name] = int(float(new_value))
                    elif isinstance(current_value, float):
                        if 'e' in new_value.lower():
                            suggested_params[param_name] = float(new_value)
                        else:
                            suggested_params[param_name] = float(new_value)
                    logger.info(f"参数建议: {param_name} = {new_value} (原值: {current_value})")
                except ValueError:
                    logger.warning(f"无法转换参数值: {new_value}")
        
        # 如果没有找到任何建议，随机调整一些参数（用于模拟模式测试）
        if suggested_params == current_params:
            logger.warning("未解析到具体参数建议，生成随机调整")
            import random
            for key in suggested_params:
                if isinstance(suggested_params[key], (int, float)) and key not in ('node_id', 'angle'):
                    # 添加 -10% 到 +20% 的随机变化
                    factor = 1 + random.uniform(-0.1, 0.2)
                    if isinstance(suggested_params[key], int):
                        suggested_params[key] = int(suggested_params[key] * factor)
                    else:
                        suggested_params[key] = suggested_params[key] * factor
                    logger.info(f"随机调整参数: {key} = {suggested_params[key]}")
        
        return suggested_params

    def condense_experience(self, start_iteration, end_iteration):
        """
        浓缩多次迭代的经验
        
        Args:
            start_iteration: 起始迭代序号
            end_iteration: 结束迭代序号
            
        Returns:
            str: 浓缩的经验总结
        """
        logger.info(f"浓缩迭代 {start_iteration} 到 {end_iteration} 的经验")
        
        # 如果处于模拟模式，返回假的经验总结
        if self.use_simulation:
            return (
                "在之前的迭代中，我们发现增加Tdrift和减小Wg参数对提高闩锁电压有积极影响，"
                "同时适当增加Wtot也能改善器件对单粒子效应的抵抗能力。"
                "但需注意增大体尺寸会带来能量消耗的增加。"
            )
        
        # 收集各个迭代的Prompts和Responses
        experiences = []
        
        for i in range(start_iteration, end_iteration + 1):
            prompt_file = self.prompts_dir / f"prompt_iteration_{i}.json"
            response_file = self.responses_dir / f"response_iteration_{i}.json"
            
            if prompt_file.exists() and response_file.exists():
                try:
                    with open(prompt_file, "r", encoding="utf-8") as f:
                        prompt = json.load(f)
                    
                    with open(response_file, "r", encoding="utf-8") as f:
                        response = json.load(f)
                    
                    # 提取关键内容
                    prompt_content = ""
                    for message in prompt:
                        if message.get("role") == "user":
                            prompt_content = message.get("content", "")
                            break
                    
                    # 去除冗长的代码部分
                    import re
                    prompt_content = re.sub(r'```.*?```', '(代码片段)', prompt_content, flags=re.DOTALL)
                    
                    # 只保留参数和结果部分
                    param_part = ""
                    result_part = ""
                    
                    if "## 当前参数" in prompt_content and "## 仿真结果" in prompt_content:
                        param_section = prompt_content.split("## 当前参数")[1].split("##")[0]
                        param_part = f"迭代{i}参数: {param_section.strip()}"
                    
                    if "## 仿真结果" in prompt_content:
                        result_section = prompt_content.split("## 仿真结果")[1].split("##")[0]
                        result_part = f"迭代{i}结果: {result_section.strip()}"
                    
                    # 将响应中的建议部分提取出来
                    suggestion_part = f"迭代{i}建议: {response[:200]}..."
                    
                    experience = f"{param_part}\n{result_part}\n{suggestion_part}\n"
                    experiences.append(experience)
                    
                except Exception as e:
                    logger.warning(f"处理迭代 {i} 的经验时出错: {str(e)}")
        
        # 如果没有收集到任何经验，返回空字符串
        if not experiences:
            return ""
        
        # 将收集到的经验合并
        combined_experience = "\n".join(experiences)
        
        # 使用DeepSeek AI浓缩经验
        system_prompt = "你是一位专业的TCAD仿真专家和数据分析师。请分析历次仿真结果和参数调整经验，提炼出关键见解。"
        user_prompt = f"""下面是过去几次仿真迭代的经验数据，包括参数设置、结果和建议。请帮我分析这些数据，总结出有价值的经验和趋势：

{combined_experience}

请提取这些迭代中的关键趋势、规律和有效的参数调整策略，浓缩成一段简短但有见地的总结。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 调用API获取浓缩的经验
        condensed_experience = self._call_api(messages)
        
        # 保存浓缩的经验
        condensed_file = self.condensed_dir / f"condensed_{start_iteration}_{end_iteration}.txt"
        with open(condensed_file, "w", encoding="utf-8") as f:
            f.write(condensed_experience)
        logger.info(f"已保存浓缩经验到: {condensed_file}")
        
        return condensed_experience 