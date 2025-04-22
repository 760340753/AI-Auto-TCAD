#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API适配器 - 使用Markdown格式进行交互
"""
import os
import re
import logging
import time
from pathlib import Path
from openai import OpenAI

logger = logging.getLogger("auto_sim.deepseek_markdown")

class DeepSeekMarkdown:
    """通过Markdown格式与DeepSeek API交互的类"""
    
    def __init__(self, project_path, api_key=None, model="Pro/deepseek-ai/DeepSeek-R1", use_simulation=False):
        """
        初始化DeepSeekMarkdown实例
        
        Args:
            project_path (str): 项目路径，用于保存提示和响应
            api_key (str, optional): DeepSeek API密钥
            model (str, optional): 使用的模型名称，默认为Pro/deepseek-ai/DeepSeek-R1
            use_simulation (bool, optional): 是否使用模拟模式，默认为False
        """
        self.project_path = Path(project_path)
        self.api_key = api_key
        self.model = model
        self.use_simulation = use_simulation
        
        # 设置保存目录
        self.deepseek_dir = self.project_path / "DeepSeek"
        self.prompts_dir = self.deepseek_dir / "Prompts"
        self.responses_dir = self.deepseek_dir / "Responses"
        
        # 创建目录
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)
        
        # 如果不使用模拟模式，创建API客户端
        if not use_simulation and api_key:
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.siliconflow.cn/v1",
                    timeout=60.0
                )
                logger.info(f"已初始化OpenAI客户端，使用模型: {model}")
            except Exception as e:
                logger.error(f"初始化OpenAI客户端失败: {str(e)}")
                self.client = None
                self.use_simulation = True
        else:
            self.client = None
            if use_simulation:
                logger.info("使用模拟模式")
            else:
                logger.warning("未提供API密钥，将使用模拟模式")
                self.use_simulation = True
    
    def get_optimization_suggestions(self, iteration, params, simulation_results, sde_code=None, sdevice_code=None):
        """
        获取参数优化建议
        
        Args:
            iteration (int): 迭代次数
            params (dict): 当前参数
            simulation_results (dict): 仿真结果
            sde_code (str, optional): SDE代码片段
            sdevice_code (str, optional): SDevice代码片段
            
        Returns:
            dict: 优化建议
        """
        # 构建系统提示词
        system_prompt = """你是一位半导体器件物理和辐射效应专家，熟悉TCAD仿真和SEE效应。
请以Markdown格式回答问题，不要使用JSON格式。

当需要提供参数优化建议时，请严格按照以下Markdown格式输出参数值：

```
## 参数优化建议

### 几何参数
- Wtot: [数值] 微米
- Wg: [数值] 微米
- Tdrift: [数值] 微米

### 掺杂参数
- NWell: [数值] cm^-3
- NDrift: [数值] cm^-3

### 工艺参数
- TOX: [数值] 纳米
- 退火温度: [数值] 摄氏度
```

请确保所有数值合理且基于TCAD仿真经验。不要添加JSON格式的内容。
提供的数值应当是确切的数字，不要使用范围或比例。
"""
        
        # 构建用户提示词
        user_prompt = f"""这是第{iteration}次TCAD单粒子效应(SEE)仿真，请基于当前参数和结果，提出优化建议。

当前参数：
- Wtot: {params.get('Wtot', 'N/A')} 微米
- Wg: {params.get('Wg', 'N/A')} 微米
- Tdrift: {params.get('Tdrift', 'N/A')} 微米
- NWell: {params.get('NWell', 'N/A')} cm^-3
- NDrift: {params.get('NDrift', 'N/A')} cm^-3
- TOX: {params.get('TOX', 'N/A')} 纳米
- 退火温度: {params.get('Temperature', 'N/A')} 摄氏度

仿真结果：
- 闩锁状态: {simulation_results.get('latchup', 'N/A')}
- 闩锁电压: {simulation_results.get('latch_voltage', 'N/A')} V
- 峰值电流: {simulation_results.get('peak_current', 'N/A')} A
- 电荷收集: {simulation_results.get('charge_collection', 'N/A')} fC
- 能量消耗: {simulation_results.get('energy_consumption', 'N/A')} J

请分析并给出优化后的参数，确保使用Markdown格式，不要使用JSON格式。优化目标是：减少电荷收集，提高闩锁电压。"""
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 保存提示
        prompt_file = self.prompts_dir / f"prompt_iteration_{iteration}.md"
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(f"# 系统提示\n\n{system_prompt}\n\n# 用户提示\n\n{user_prompt}")
        logger.info(f"已保存提示到: {prompt_file}")
        
        # 获取响应
        if self.use_simulation or not self.client:
            response_text = self._get_simulated_response(params)
        else:
            try:
                start_time = time.time()
                logger.info(f"正在调用DeepSeek API，使用模型: {self.model}")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000,
                    timeout=60.0
                )
                
                elapsed_time = time.time() - start_time
                logger.info(f"API响应收到，耗时: {elapsed_time:.2f}秒")
                
                response_text = response.choices[0].message.content
                if not response_text.strip():
                    logger.warning("API返回了空响应，使用模拟响应")
                    response_text = self._get_simulated_response(params)
            except Exception as e:
                logger.error(f"API调用失败: {str(e)}")
                logger.warning("使用模拟响应作为备选")
                response_text = self._get_simulated_response(params)
        
        # 保存响应
        response_file = self.responses_dir / f"response_iteration_{iteration}.md"
        with open(response_file, "w", encoding="utf-8") as f:
            f.write(response_text)
        logger.info(f"已保存响应到: {response_file}")
        
        # 解析参数
        suggested_params = self._parse_markdown_response(response_text, params)
        
        return suggested_params
    
    def _get_simulated_response(self, params):
        """
        获取模拟响应
        
        Args:
            params (dict): 当前参数
            
        Returns:
            str: 模拟响应文本
        """
        # 生成略微调整的参数
        import random
        random.seed(time.time())  # 使用当前时间作为随机种子
        
        wtot = params.get('Wtot', 50) * random.uniform(0.9, 1.1)
        wg = params.get('Wg', 10) * random.uniform(0.9, 1.1)
        tdrift = params.get('Tdrift', 300) * random.uniform(0.9, 1.1)
        nwell = params.get('NWell', 5e17) * random.uniform(0.9, 1.1)
        ndrift = params.get('NDrift', 1e14) * random.uniform(1.0, 1.2)
        tox = params.get('TOX', 50) * random.uniform(0.9, 1.1)
        temp = params.get('Temperature', 900) * random.uniform(0.95, 1.05)
        
        # 生成模拟响应
        return f"""
## SEE效应优化策略分析

通过分析当前参数和仿真结果，发现主要问题在于电荷收集效率过高和闩锁电压较低。针对这些问题，提出以下优化建议。

## 参数优化建议

### 几何参数
- Wtot: {wtot:.2f} 微米
- Wg: {wg:.2f} 微米
- Tdrift: {tdrift:.2f} 微米

### 掺杂参数
- NWell: {nwell:.2e} cm^-3
- NDrift: {ndrift:.2e} cm^-3

### 工艺参数
- TOX: {tox:.2f} 纳米
- 退火温度: {temp:.2f} 摄氏度

## 参数调整分析

1. **Wtot增加**：扩大总宽度有助于改善电流分布，减少局部热点，提高闩锁阈值。
2. **Tdrift减小**：减少漂移区厚度可以缩短电荷收集路径，降低总电荷收集量。
3. **NDrift提高**：增加漂移区掺杂浓度可以减少耗尽区宽度，降低电荷收集效率。
4. **NWell调整**：适当降低阱区掺杂可以提高结电压，改善闩锁特性。
5. **TOX优化**：调整氧化层厚度可以优化电场分布，减轻表面效应的影响。

这些参数调整综合考虑了器件性能和抗辐射能力的平衡。建议进行下一轮仿真验证效果。
"""
    
    def _parse_markdown_response(self, response_text, current_params):
        """
        从Markdown响应中解析参数
        
        Args:
            response_text (str): 响应文本
            current_params (dict): 当前参数
            
        Returns:
            dict: 解析的参数
        """
        # 复制当前参数作为基础
        suggested_params = current_params.copy()
        
        # 定义参数匹配模式
        patterns = {
            'Wtot': r'Wtot:\s*(\d+\.?\d*)',
            'Wg': r'Wg:\s*(\d+\.?\d*)',
            'Tdrift': r'Tdrift:\s*(\d+\.?\d*)',
            'NWell': r'NWell:\s*(\d+\.?\d*e[+-]?\d+|\d+\.?\d*)',
            'NDrift': r'NDrift:\s*(\d+\.?\d*e[+-]?\d+|\d+\.?\d*)',
            'TOX': r'TOX:\s*(\d+\.?\d*)',
            'Temperature': r'退火温度:\s*(\d+\.?\d*)'
        }
        
        # 查找并解析参数
        for param_name, pattern in patterns.items():
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                value_str = match.group(1)
                try:
                    # 根据参数类型进行转换
                    if param_name in ('NWell', 'NDrift'):
                        value = float(value_str)
                    elif param_name in ('Wtot', 'Wg', 'Tdrift', 'TOX', 'Temperature'):
                        value = float(value_str)
                    else:
                        value = value_str
                    
                    suggested_params[param_name] = value
                    logger.info(f"从响应中解析参数: {param_name} = {value}")
                except ValueError:
                    logger.warning(f"无法解析参数值: {param_name} = {value_str}")
        
        # 返回解析后的参数
        return suggested_params
    
    def analyze_simulation_results(self, iteration, simulation_results):
        """
        分析仿真结果
        
        Args:
            iteration (int): 迭代次数
            simulation_results (dict): 仿真结果
            
        Returns:
            str: 分析结果
        """
        # 构建系统提示词
        system_prompt = """你是一位半导体器件物理和辐射效应专家，熟悉TCAD仿真和SEE效应。
请分析TCAD仿真的结果，提供专业见解。
回复必须使用Markdown格式，包含以下几部分：
1. 结果总结 - 简要概述仿真结果
2. 关键发现 - 分析结果中的重要现象和趋势
3. 改进建议 - 提出可能的改进方向

请保持专业性和具体性，避免泛泛而谈。
"""
        
        # 构建用户提示词
        user_prompt = f"""这是第{iteration}次TCAD单粒子效应(SEE)仿真的结果，请进行专业分析：

仿真结果：
- 闩锁状态: {simulation_results.get('latchup', 'N/A')}
- 闩锁电压: {simulation_results.get('latch_voltage', 'N/A')} V
- 峰值电流: {simulation_results.get('peak_current', 'N/A')} A
- 电荷收集: {simulation_results.get('charge_collection', 'N/A')} fC
- 能量消耗: {simulation_results.get('energy_consumption', 'N/A')} J

请分析这些结果，并提供专业见解。"""
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 保存提示
        prompt_file = self.prompts_dir / f"analysis_prompt_iteration_{iteration}.md"
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(f"# 系统提示\n\n{system_prompt}\n\n# 用户提示\n\n{user_prompt}")
        
        # 获取响应
        if self.use_simulation or not self.client:
            analysis = self._get_simulated_analysis(simulation_results)
        else:
            try:
                logger.info(f"正在调用DeepSeek API获取分析，使用模型: {self.model}")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000,
                    timeout=60.0
                )
                
                analysis = response.choices[0].message.content
                if not analysis.strip():
                    logger.warning("API返回了空响应，使用模拟分析")
                    analysis = self._get_simulated_analysis(simulation_results)
            except Exception as e:
                logger.error(f"API调用失败: {str(e)}")
                logger.warning("使用模拟分析作为备选")
                analysis = self._get_simulated_analysis(simulation_results)
        
        # 保存响应
        response_file = self.responses_dir / f"analysis_iteration_{iteration}.md"
        with open(response_file, "w", encoding="utf-8") as f:
            f.write(analysis)
        
        return analysis
    
    def _get_simulated_analysis(self, simulation_results):
        """
        获取模拟分析
        
        Args:
            simulation_results (dict): 仿真结果
            
        Returns:
            str: 模拟分析文本
        """
        latchup = simulation_results.get('latchup', False)
        latch_voltage = simulation_results.get('latch_voltage', 'N/A')
        peak_current = simulation_results.get('peak_current', 'N/A')
        charge_collection = simulation_results.get('charge_collection', 'N/A')
        
        if latchup:
            return f"""
# TCAD SEE仿真结果分析

## 结果总结
当前仿真显示器件发生了闩锁现象，闩锁电压为{latch_voltage}V，峰值电流为{peak_current}A，电荷收集为{charge_collection}fC。这表明器件在单粒子效应下的抗辐射性能不足。

## 关键发现
1. **闩锁现象确认**：器件在辐射粒子作用下出现了闩锁，这是设计中需要避免的严重问题
2. **电荷收集过高**：{charge_collection}fC的电荷收集量表明器件对辐射粒子过于敏感
3. **闩锁电压不足**：{latch_voltage}V的闩锁电压低于工业应用标准，存在可靠性风险

## 改进建议
1. 优化器件结构以提高闩锁电压，可考虑增加阱区间距或引入额外的保护结构
2. 调整掺杂分布，特别是提高漂移区掺杂以减少电荷收集
3. 考虑在关键区域引入深沟槽隔离，以抑制寄生晶体管效应
4. 探索脉冲退火工艺，提高界面质量，减少载流子陷阱
"""
        else:
            return f"""
# TCAD SEE仿真结果分析

## 结果总结
当前仿真显示器件未发生闩锁现象，峰值电流为{peak_current}A，电荷收集为{charge_collection}fC。这表明器件具有一定的抗单粒子效应能力。

## 关键发现
1. **未发生闩锁**：器件在当前辐射条件下保持了正常工作状态，这是设计的积极成果
2. **电荷收集情况**：{charge_collection}fC的电荷收集量在同类器件中处于中等水平
3. **峰值电流可控**：{peak_current}A的峰值电流未导致热失控或触发寄生结构

## 改进建议
1. 进一步优化掺杂分布，降低电荷收集总量
2. 考虑减薄漂移区厚度，在维持足够耐压的前提下减少电荷收集路径
3. 探索引入埋层结构，以改善电场分布和载流子输运
4. 建议进行更高LET条件下的仿真验证，确保在更极端条件下的抗辐射能力
""" 