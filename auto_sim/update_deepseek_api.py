#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新DeepSeekInteraction类以使用siliconflow API
"""
import os
import sys
import shutil
from pathlib import Path

def backup_original_file(file_path):
    """创建原始文件的备份"""
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    print(f"已创建原始文件备份: {backup_path}")
    return backup_path

def update_deepseek_interaction(file_path):
    """更新DeepSeekInteraction类以使用siliconflow API"""
    # 读取原始文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查文件是否包含DeepSeekInteraction类
    if "class DeepSeekInteraction" not in content:
        print(f"错误：文件 {file_path} 中未发现DeepSeekInteraction类")
        return False
    
    # 创建备份
    backup_original_file(file_path)
    
    # 更新init方法
    init_method = '''    def __init__(self, api_key=None, api_url=None, use_siliconflow=False):
        """
        初始化DeepSeek交互
        
        Args:
            api_key: DeepSeek API密钥，如未提供则从环境变量DEEPSEEK_API_KEY获取
            api_url: DeepSeek API URL，如未提供则使用默认URL
            use_siliconflow: 是否使用siliconflow API
        """
        self.api_key = api_key if api_key else os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            logger.warning("未提供DeepSeek API密钥，将使用模拟模式")
        
        # 使用siliconflow API
        self.use_siliconflow = use_siliconflow
        if use_siliconflow:
            self.api_url = api_url if api_url else "https://api.siliconflow.cn/v1"
            self.model = "Pro/deepseek-ai/DeepSeek-R1"
        else:
            self.api_url = api_url if api_url else "https://api.deepseek.com/v1/chat/completions"
        
        # 缓存目录
        self.cache_dir = Path("./deepseek_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 历史记录
        self.conversation_history = []
        
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
            self.client = None'''
    
    # 更新_call_api方法
    call_api_method = '''    def _call_api(self, messages):
        """
        调用DeepSeek API
        
        Args:
            messages: 消息列表，包含角色和内容
            
        Returns:
            str: API响应内容
        """
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
                print(f"API响应成功，内容长度：{len(content)}")
                print(f"内容预览：{content[:100]}...")
                return content
                
            except Exception as e:
                error_msg = f"调用siliconflow API时出错: {str(e)}"
                logger.error(error_msg)
                print(error_msg)
                # 在错误时，仍然提供模拟响应，但记录错误
                print("由于API调用失败，使用模拟响应代替")
                return self._simulate_api_response(messages)
                
        # 如果不使用siliconflow，使用原有的API调用方式
        print(f"使用API密钥：{self.api_key[:5]}...{self.api_key[-5:]}")
        assert self.api_key, "API密钥不能为空"
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            print(f"调用DeepSeek API，URL: {self.api_url}")
            print(f"请求头：包含Authorization: Bearer {self.api_key[:5]}...{self.api_key[-5:]}")
            print(f"请求数据：包含{len(messages)}条消息")
            print(f"系统提示：{messages[0].get('content', '')[:50]}...")
            print(f"用户消息：{messages[-1].get('content', '')[:50]}...")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=120  # 增加超时时间
            )
            
            print(f"API响应状态码: {response.status_code}")
            print(f"API响应头: {response.headers}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"API响应成功，内容长度：{len(result.get('choices', [{}])[0].get('message', {}).get('content', ''))}")
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                print(f"内容预览：{content[:100]}...")
                return content
            else:
                error_msg = f"API调用失败: {response.status_code}, {response.text}"
                logger.error(error_msg)
                print(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            error_msg = f"调用API时出错: {str(e)}"
            logger.error(error_msg)
            print(error_msg)
            # 在错误时，仍然提供模拟响应，但记录错误
            print("由于API调用失败，使用模拟响应代替")
            return self._simulate_api_response(messages)'''
    
    # 替换文件内容
    updated_content = content
    
    # 替换init方法
    import re
    init_pattern = r'def __init__\s*\([^)]*\):.*?(?=\n    def )'
    updated_content = re.sub(init_pattern, init_method, updated_content, flags=re.DOTALL)
    
    # 替换_call_api方法
    call_api_pattern = r'def _call_api\s*\([^)]*\):.*?(?=\n    def )'
    updated_content = re.sub(call_api_pattern, call_api_method, updated_content, flags=re.DOTALL)
    
    # 添加导入
    if "from openai import OpenAI" not in updated_content:
        # 在import部分添加OpenAI导入
        import_pattern = r'(import [^\n]*\n)+'
        openai_import = 'from openai import OpenAI\n'
        match = re.search(import_pattern, updated_content)
        if match:
            imports_end = match.end()
            updated_content = updated_content[:imports_end] + openai_import + updated_content[imports_end:]
    
    # 写入更新后的内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"已更新文件: {file_path}")
    return True

def main():
    """主函数"""
    print("DeepSeekInteraction类更新工具")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 默认位置
        file_path = "./auto_sim/deepseek_interaction.py"
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误：文件 {file_path} 不存在")
        return 1
    
    # 更新文件
    success = update_deepseek_interaction(file_path)
    
    if success:
        print("\n更新成功！")
        print("\n请在配置文件中添加use_siliconflow=True选项以启用siliconflow API")
        print("例如，在配置文件中添加：")
        print('''
{
    "api_key": "YOUR_API_KEY_FROM_CLOUD_SILICONFLOW_CN",
    "use_siliconflow": true,
    ...其他配置...
}
''')
        return 0
    else:
        print("\n更新失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 