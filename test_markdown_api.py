#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：使用Markdown格式直接测试DeepSeek API
"""

import os
import sys
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
API_KEY = "sk-buspthftjrkhcudljfardlbubjlmpfoxehgstdipajrxpccc"  # 使用提供的API密钥

def test_markdown_api():
    """使用Markdown格式测试DeepSeek API"""
    
    # 系统提示
    system_prompt = """你是一个专业的半导体器件TCAD仿真优化专家。基于用户提供的仿真参数和结果，你需要提出下一次迭代的参数优化建议。
    
参数必须按以下Markdown格式返回（不要添加任何其他内容）：

```parameters
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

其中每个参数必须是一个浮点数。"""

    # 用户提示（使用Markdown格式）
    user_message = """## 当前仿真参数
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

## 目标
- 提高闩锁电压至1000V以上
- 减小峰值电流
- 优化电荷收集和能量消耗

请根据以上信息，提供下一次仿真迭代的参数优化建议。"""

    # 构建请求消息
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    # 构建请求数据
    request_data = {
        "model": "deepseek-ai/deepseek-chat-v1", # 使用DeepSeek的聊天模型
        "messages": messages,
        "temperature": 0.0, # 设置为0以获得确定性输出
        "response_format": {"type": "text"} # 确保输出为文本格式
    }
    
    # 打印请求信息
    logger.info(f"API密钥（掩码）: {API_KEY[:5]}...{API_KEY[-5:]}")
    logger.info(f"API URL: {API_URL}")
    logger.info(f"请求头: Authorization: Bearer sk-****")
    logger.info(f"请求模型: {request_data['model']}")
    logger.info(f"请求温度: {request_data['temperature']}")
    logger.info(f"系统提示预览: {system_prompt[:100]}...")
    logger.info(f"用户消息预览: {user_message[:100]}...")
    
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
        logger.info(f"API响应头: {dict(response.headers)}")
        
        # 检查是否成功
        if response.status_code == 200:
            response_data = response.json()
            logger.info("API调用成功")
            logger.info(f"响应内容长度: {len(str(response_data))}")
            
            # 获取并打印响应内容
            content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            logger.info(f"响应内容:\n{content}")
            
            # 保存结果到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"deepseek_markdown_response_{timestamp}.md", "w") as f:
                f.write(content)
            logger.info(f"响应已保存到文件: deepseek_markdown_response_{timestamp}.md")
            
            return content
        else:
            logger.error(f"API调用失败: {response.status_code} - {response.text}")
            return f"API调用失败: {response.status_code} - {response.text}"
    
    except Exception as e:
        logger.error(f"发生异常: {str(e)}")
        return f"异常: {str(e)}"

if __name__ == "__main__":
    logger.info("开始测试DeepSeek API的Markdown格式交互...")
    result = test_markdown_api()
    logger.info("测试完成") 