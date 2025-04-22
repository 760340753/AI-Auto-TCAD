#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试siliconflow.cn的DeepSeek API
"""
from openai import OpenAI
import os
from pathlib import Path

# 请替换为您的真实API密钥
API_KEY = "在此处填入您的API密钥"

def main():
    print("=" * 60)
    print("简单测试siliconflow.cn的DeepSeek API")
    print("=" * 60)
    
    # 检查API密钥
    if API_KEY == "sk-buspthftjrkhcudljfardlbubjlmpfoxehgstdipajrxpccc": #"在此处填入您的API密钥":
        print("错误：请先在脚本中设置您的API密钥")
        return
    
    # 创建OpenAI客户端
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.siliconflow.cn/v1"
    )
    
    # 简单查询
    query = "在TCAD仿真中，如何优化单粒子效应(SEE)的抗性？请简单列出3点建议。"
    
    print(f"发送查询: {query}")
    print("正在调用API，请稍等...")
    
    try:
        # 调用API
        response = client.chat.completions.create(
            model="Pro/deepseek-ai/DeepSeek-R1",
            messages=[
                {"role": "system", "content": "你是一位半导体器件物理和辐射效应专家。"},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # 获取响应
        content = response.choices[0].message.content
        
        print("\n响应内容:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        
        # 保存响应
        result_dir = Path("./DeepSeek/Responses")
        result_dir.mkdir(parents=True, exist_ok=True)
        
        with open(result_dir / "simple_test_response.txt", "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"响应已保存到: {result_dir / 'simple_test_response.txt'}")
        print("API测试成功！")
        
    except Exception as e:
        print(f"API调用出错: {str(e)}")
        print("请确认您的API密钥是否正确，以及网络连接是否正常")

if __name__ == "__main__":
    main() 
