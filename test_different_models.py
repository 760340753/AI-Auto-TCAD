#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：测试多种DeepSeek模型和请求格式
"""

import os
import json
import logging
import requests
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# DeepSeek API 配置
API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = "sk-buspthftjrkhcudljfardlbubjlmpfoxehgstdipajrxpccc"

def test_api_call(model_name, test_name, format_type="default"):
    """测试不同模型和格式的API调用"""
    
    # 系统提示 - 根据格式类型选择
    if format_type == "markdown":
        system_prompt = """# TCAD仿真优化专家

你是一个专业的半导体器件TCAD仿真优化专家。根据用户提供的仿真参数和结果，提出下一次迭代的参数优化建议。

## 输出格式要求

你必须严格按照以下Markdown格式返回参数：

```
Wtot: <float>
Wg: <float>
Tdrift: <float>
Tox: <float>
Tpoly: <float>
Tcathode: <float>
Jpeak: <float>
Tepi: <float>
Nepi: <float>
```

只返回这些参数值，不要有任何额外的解释。"""
    elif format_type == "json":
        system_prompt = """你是一个专业的半导体器件TCAD仿真优化专家。根据用户提供的仿真参数和结果，提出下一次迭代的参数优化建议。

你必须严格按照以下JSON格式返回参数，不要有任何额外的解释：

{
    "Wtot": <float>,
    "Wg": <float>,
    "Tdrift": <float>,
    "Tox": <float>,
    "Tpoly": <float>,
    "Tcathode": <float>,
    "Jpeak": <float>,
    "Tepi": <float>,
    "Nepi": <float>
}"""
    else:
        system_prompt = """你是一个专业的半导体器件TCAD仿真优化专家。基于用户提供的仿真参数和结果，你需要提出下一次迭代的参数优化建议。
    
你必须严格按照以下格式返回参数，不要有任何额外的解释或说明，只返回这些参数值：

Wtot: <float>
Wg: <float>
Tdrift: <float>
Tox: <float>
Tpoly: <float>
Tcathode: <float>
Jpeak: <float>
Tepi: <float>
Nepi: <float>"""

    # 用户提示
    if format_type == "markdown":
        user_message = """# 当前仿真数据

## 仿真参数
- Wtot: 50.0
- Wg: 10.0
- Tdrift: 330.0
- Tox: 0.05
- Tpoly: 0.5
- Tcathode: 1.0
- Jpeak: 5e19
- Tepi: 10.0
- Nepi: 1e15

## 仿真结果
- 闩锁状态: 是
- 闩锁电压: 800V
- 峰值电流: 2.5A
- 电荷收集: 1.2e-9 C
- 能量消耗: 5.6e-7 J

## 优化目标
- 提高闩锁电压至1000V以上
- 减小峰值电流
- 优化电荷收集和能量消耗

请根据以上信息，提供下一次仿真迭代的参数优化建议。"""
    elif format_type == "json":
        user_message = """{
    "current_params": {
        "Wtot": 50.0,
        "Wg": 10.0,
        "Tdrift": 330.0,
        "Tox": 0.05,
        "Tpoly": 0.5,
        "Tcathode": 1.0,
        "Jpeak": 5e19,
        "Tepi": 10.0,
        "Nepi": 1e15
    },
    "simulation_results": {
        "latchup_status": true,
        "latchup_voltage": 800,
        "peak_current": 2.5,
        "charge_collection": 1.2e-9,
        "energy_consumption": 5.6e-7
    },
    "targets": {
        "latchup_voltage": ">1000V",
        "peak_current": "minimize",
        "charge_and_energy": "optimize"
    }
}"""
    else:
        user_message = """当前仿真参数:
Wtot: 50.0
Wg: 10.0
Tdrift: 330.0
Tox: 0.05
Tpoly: 0.5
Tcathode: 1.0
Jpeak: 5e19
Tepi: 10.0
Nepi: 1e15

仿真结果:
闩锁状态: 是
闩锁电压: 800V
峰值电流: 2.5A
电荷收集: 1.2e-9 C
能量消耗: 5.6e-7 J

目标:
- 提高闩锁电压至1000V以上
- 减小峰值电流
- 优化电荷收集和能量消耗

请根据以上信息，提供下一次仿真迭代的参数优化建议。"""

    # 构建请求消息
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    # 根据模型名称设置其他请求参数
    request_data = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.0,  # 设置为0以获得确定性输出
    }
    
    # 对某些模型添加额外参数
    if "deepseek-v2" in model_name:
        request_data["max_tokens"] = 1000
    
    # 打印请求信息
    logger.info(f"测试名称: {test_name}")
    logger.info(f"模型: {model_name}")
    logger.info(f"格式类型: {format_type}")
    logger.info(f"API密钥（掩码）: {API_KEY[:5]}...{API_KEY[-5:]}")
    logger.info(f"API URL: {API_URL}")
    
    try:
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        # 发送API请求
        logger.info("发送API请求...")
        response = requests.post(
            API_URL,
            headers=headers,
            json=request_data,
            timeout=180  # 延长超时时间至3分钟
        )
        
        # 记录响应状态
        logger.info(f"API响应状态码: {response.status_code}")
        
        # 检查是否成功
        if response.status_code == 200:
            response_data = response.json()
            logger.info("API调用成功")
            
            # 获取并打印响应内容
            content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            logger.info(f"响应内容:\n{content}")
            
            # 保存结果到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"response_{test_name}_{timestamp}"
            
            if format_type == "markdown":
                filename += ".md"
            elif format_type == "json":
                filename += ".json"
            else:
                filename += ".txt"
                
            with open(filename, "w") as f:
                f.write(content)
            logger.info(f"响应已保存到文件: {filename}")
            
            return content
        else:
            error_msg = f"API调用失败: {response.status_code} - {response.text}"
            logger.error(error_msg)
            
            # 保存错误信息
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"error_{test_name}_{timestamp}.txt", "w") as f:
                f.write(error_msg)
            
            return error_msg
    
    except Exception as e:
        error_msg = f"发生异常: {str(e)}"
        logger.error(error_msg)
        
        # 保存错误信息
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"error_{test_name}_{timestamp}.txt", "w") as f:
            f.write(error_msg)
        
        return error_msg

if __name__ == "__main__":
    logger.info("开始测试不同DeepSeek模型和格式...")
    
    # 测试组合
    tests = [
        {"model": "deepseek-ai/deepseek-chat-v1", "name": "chat_v1_default", "format": "default"},
        {"model": "deepseek-ai/deepseek-chat-v1", "name": "chat_v1_markdown", "format": "markdown"},
        {"model": "deepseek-ai/deepseek-chat-v1", "name": "chat_v1_json", "format": "json"},
        
        {"model": "deepseek-ai/deepseek-v2", "name": "v2_default", "format": "default"},
        {"model": "deepseek-ai/deepseek-v2", "name": "v2_markdown", "format": "markdown"},
        {"model": "deepseek-ai/deepseek-v2", "name": "v2_json", "format": "json"},
        
        {"model": "deepseek-ai/deepseek-v2.5", "name": "v2_5_default", "format": "default"},
        
        {"model": "deepseek-ai/deepseek-coder-v2", "name": "coder_v2_default", "format": "default"},
        {"model": "deepseek-ai/deepseek-coder-v2", "name": "coder_v2_json", "format": "json"}
    ]
    
    # 执行测试
    for test in tests:
        logger.info(f"\n{'='*50}\n开始测试: {test['name']}\n{'='*50}")
        try:
            result = test_api_call(test["model"], test["name"], test["format"])
            logger.info(f"测试 {test['name']} 完成\n")
        except Exception as e:
            logger.error(f"测试 {test['name']} 出错: {str(e)}\n")
    
    logger.info("所有测试完成") 