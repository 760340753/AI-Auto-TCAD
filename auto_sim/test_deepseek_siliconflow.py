#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试通过siliconflow.cn API调用DeepSeek模型
"""
import os
import json
from pathlib import Path
from openai import OpenAI

def test_direct_api_call():
    """
    直接测试通过OpenAI库调用DeepSeek模型
    """
    print("开始测试通过OpenAI库调用DeepSeek模型...")
    
    # 请替换为您从siliconflow.cn获取的API密钥
    api_key = "请在此处输入您的真实API密钥"  # 运行前必须替换为有效的密钥
    
    # 初始化OpenAI客户端，使用siliconflow的API端点
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.siliconflow.cn/v1"
    )
    
    # 准备查询内容
    query = "在TCAD仿真中，如何优化单粒子效应(SEE)的参数设置？请给出具体建议。"
    
    try:
        print(f"\n发送API请求到siliconflow.cn，模型: Pro/deepseek-ai/DeepSeek-R1")
        print(f"查询内容: {query}")
        
        # 创建聊天完成（流式响应）
        response = client.chat.completions.create(
            model='Pro/deepseek-ai/DeepSeek-R1',
            messages=[
                {'role': 'system', 'content': "你是一位半导体器件物理和辐射效应专家，熟悉TCAD仿真和SEE效应。"},
                {'role': 'user', 'content': query}
            ],
            stream=True
        )
        
        print("\n模型响应:")
        print("-" * 50)
        
        # 处理流式响应
        full_response = ""
        for chunk in response:
            if not chunk.choices:
                continue
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
            if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                reasoning = chunk.choices[0].delta.reasoning_content
                print(reasoning, end="", flush=True)
                full_response += reasoning
                
        print("\n" + "-" * 50)
        
        # 保存响应到文件
        output_dir = Path("./DeepSeek/Responses")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "siliconflow_response.txt", "w", encoding="utf-8") as f:
            f.write(full_response)
            
        print(f"\n响应已保存到: {output_dir / 'siliconflow_response.txt'}")
        print("\nAPI调用测试完成")
        
    except Exception as e:
        print(f"\nAPI调用出错: {str(e)}")
        import traceback
        traceback.print_exc()

def test_non_streaming_call():
    """
    测试非流式API调用
    """
    print("开始测试非流式API调用...")
    
    # 请替换为您从siliconflow.cn获取的API密钥
    api_key = "请在此处输入您的真实API密钥"  # 运行前必须替换为有效的密钥
    
    # 初始化OpenAI客户端，使用siliconflow的API端点
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.siliconflow.cn/v1"
    )
    
    # 准备查询内容
    query = "在TCAD仿真中，如何优化参数以提高电荷收集效率？请简要列出3点建议。"
    
    try:
        print(f"\n发送非流式API请求，模型: Pro/deepseek-ai/DeepSeek-R1")
        print(f"查询内容: {query}")
        
        # 创建聊天完成（非流式响应）
        response = client.chat.completions.create(
            model='Pro/deepseek-ai/DeepSeek-R1',
            messages=[
                {'role': 'system', 'content': "你是一位半导体器件物理和辐射效应专家，熟悉TCAD仿真和SEE效应。"},
                {'role': 'user', 'content': query}
            ],
            stream=False
        )
        
        # 获取并打印完整响应
        content = response.choices[0].message.content
        print("\n模型响应:")
        print("-" * 50)
        print(content)
        print("-" * 50)
        
        # 保存响应到文件
        output_dir = Path("./DeepSeek/Responses")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "siliconflow_non_stream_response.txt", "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"\n响应已保存到: {output_dir / 'siliconflow_non_stream_response.txt'}")
        print("\n非流式API调用测试完成")
        
    except Exception as e:
        print(f"\nAPI调用出错: {str(e)}")
        import traceback
        traceback.print_exc()

def update_deepseek_interaction():
    """
    演示如何更新现有的DeepSeekInteraction类以使用siliconflow API
    """
    print("\n以下是更新现有DeepSeekInteraction类以使用siliconflow API的示例代码:")
    print("-" * 50)
    code_example = '''
# 在DeepSeekInteraction类中添加使用siliconflow API的支持
def __init__(self, api_key=None, api_url=None, use_siliconflow=False):
    """初始化DeepSeek交互"""
    self.api_key = api_key if api_key else os.environ.get("DEEPSEEK_API_KEY")
    if not self.api_key:
        logger.warning("未提供API密钥，将使用模拟模式")
        
    # 使用siliconflow API
    self.use_siliconflow = use_siliconflow
    if use_siliconflow:
        self.api_url = api_url if api_url else "https://api.siliconflow.cn/v1"
        self.model = "Pro/deepseek-ai/DeepSeek-R1"
    else:
        self.api_url = api_url if api_url else "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
    
    # 初始化OpenAI客户端（如果使用siliconflow）
    if use_siliconflow and self.api_key:
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_url
            )
            logger.info(f"已初始化OpenAI客户端，使用端点: {self.api_url}")
        except ImportError:
            logger.error("未安装OpenAI库，无法使用siliconflow API")
            self.client = None
    else:
        self.client = None
    
    # 其他初始化代码...

def _call_api(self, messages):
    """调用DeepSeek API"""
    if not self.api_key:
        print("警告：未提供API密钥，使用模拟响应")
        return self._simulate_api_response(messages)
    
    # 使用siliconflow API
    if self.use_siliconflow and self.client:
        try:
            print(f"使用siliconflow API调用DeepSeek模型: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": m["role"], "content": m["content"]} 
                    for m in messages
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return content
            
        except Exception as e:
            error_msg = f"调用siliconflow API时出错: {str(e)}"
            logger.error(error_msg)
            print(error_msg)
            return self._simulate_api_response(messages)
    
    # 如果不使用siliconflow，使用原有的API调用方式
    # 原有的API调用代码...
'''
    print(code_example)
    print("-" * 50)

if __name__ == "__main__":
    print("DeepSeek API通过siliconflow.cn测试脚本")
    print("=" * 60)
    print("请在运行前将API密钥替换为您从siliconflow.cn获取的真实密钥")
    print("=" * 60)
    
    # 列出可用的测试函数
    print("\n可用测试选项:")
    print("1. 测试流式API调用")
    print("2. 测试非流式API调用")
    print("3. 查看如何更新DeepSeekInteraction类")
    
    choice = input("\n请选择要运行的测试 (1/2/3)，或按Enter运行所有测试: ")
    
    if choice == "1":
        test_direct_api_call()
    elif choice == "2":
        test_non_streaming_call()
    elif choice == "3":
        update_deepseek_interaction()
    else:
        # 运行所有测试
        test_direct_api_call()
        print("\n" + "=" * 60 + "\n")
        test_non_streaming_call()
        print("\n" + "=" * 60 + "\n")
        update_deepseek_interaction() 