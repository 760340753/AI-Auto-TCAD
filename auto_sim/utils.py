#!/usr/bin/env python3
"""
工具函数模块
"""

import json
import random
from typing import Dict, Any, List

def simulate_response(model_name: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
    """
    模拟API响应，用于测试和开发
    
    Args:
        model_name: 模型名称
        messages: 消息列表
        **kwargs: 其他参数
        
    Returns:
        模拟的API响应
    """
    # 从消息中提取用户查询
    user_message = next((m["content"] for m in messages if m["role"] == "user"), "")
    
    # 解析用户查询中的参数
    params = {}
    current_params_section = False
    for line in user_message.split("\n"):
        if "## 当前参数" in line:
            current_params_section = True
            continue
        if current_params_section and line.startswith("## "):
            current_params_section = False
            continue
        if current_params_section and line.startswith("- "):
            parts = line[2:].split(":")
            if len(parts) == 2:
                param_name = parts[0].strip()
                try:
                    param_value = float(parts[1].strip())
                    params[param_name] = param_value
                except ValueError:
                    pass
    
    # 生成随机调整的参数
    suggestions = {}
    for param, value in params.items():
        # 随机调整±20%
        adjustment = 0.8 + 0.4 * random.random()
        suggestions[param] = round(value * adjustment, 6)
    
    # 根据模型返回不同格式的响应
    if "pro" in model_name.lower():
        # 返回Markdown格式
        content = "# 参数优化建议\n\n根据您的模拟结果，我建议以下参数调整：\n\n"
        content += "| 参数 | 建议值 |\n|------|--------|\n"
        for param, value in suggestions.items():
            content += f"| {param} | {value} |\n"
    else:
        # 返回JSON格式
        content = json.dumps(suggestions, indent=2)
    
    # 构建完整响应
    return {
        "id": f"sim_chatcmpl_{random.randint(1000, 9999)}",
        "object": "chat.completion",
        "created": 1683000000,
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 100,
            "total_tokens": 200
        }
    } 