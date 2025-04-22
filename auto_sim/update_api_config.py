#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新配置文件以使用siliconflow的DeepSeek API (Markdown格式)
"""
import os
import json
import argparse
from pathlib import Path

def update_config(config_path, api_key=None, use_markdown=True, model=None):
    """
    更新配置文件以使用siliconflow的DeepSeek API
    
    Args:
        config_path (str): 配置文件路径
        api_key (str, optional): DeepSeek API密钥
        use_markdown (bool, optional): 是否使用Markdown格式，默认为True
        model (str, optional): 使用的模型名称
    
    Returns:
        bool: 是否成功更新
    """
    # 检查配置文件是否存在
    config_path = Path(config_path)
    if not config_path.exists():
        print(f"错误：配置文件 {config_path} 不存在")
        return False
    
    # 读取配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"读取配置文件失败: {str(e)}")
        return False
    
    # 备份原始配置文件
    backup_path = config_path.with_suffix(f'{config_path.suffix}.bak')
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"已备份原始配置文件到：{backup_path}")
    except Exception as e:
        print(f"备份配置文件失败: {str(e)}")
        return False
    
    # 更新配置
    if api_key:
        config['api_key'] = api_key
    
    # 添加新的配置项
    config['use_siliconflow'] = True
    config['use_markdown'] = use_markdown
    
    if model:
        config['model'] = model
    elif 'model' not in config:
        # 如果未指定模型且配置中没有模型，使用默认模型
        if use_markdown:
            # 使用Markdown格式时，推荐使用Pro/deepseek-ai/DeepSeek-R1
            config['model'] = "Pro/deepseek-ai/DeepSeek-R1"
        else:
            # 不使用Markdown格式时，使用Qwen模型作为备选
            config['model'] = "Qwen/Qwen2.5-7B-Instruct"
    
    # 写入更新后的配置
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"已更新配置文件：{config_path}")
    except Exception as e:
        print(f"更新配置文件失败: {str(e)}")
        return False
    
    return True

def create_config_if_not_exists(config_path, api_key=None):
    """
    如果配置文件不存在，创建默认配置
    
    Args:
        config_path (str): 配置文件路径
        api_key (str, optional): DeepSeek API密钥
    
    Returns:
        bool: 是否成功创建
    """
    config_path = Path(config_path)
    if config_path.exists():
        return True
    
    # 创建默认配置
    default_config = {
        "api_key": api_key if api_key else "YOUR_API_KEY_HERE",
        "use_siliconflow": True,
        "use_markdown": True,
        "model": "Pro/deepseek-ai/DeepSeek-R1",
        "max_iterations": 10,
        "target_voltage": 700,
        "target_charge_collection": 8.0
    }
    
    # 创建目录(如果不存在)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入配置文件
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        print(f"已创建默认配置文件：{config_path}")
        return True
    except Exception as e:
        print(f"创建配置文件失败: {str(e)}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='更新配置文件以使用siliconflow的DeepSeek API')
    parser.add_argument('--config', type=str, default='./auto_sim_config.json', help='配置文件路径')
    parser.add_argument('--api-key', type=str, help='DeepSeek API密钥')
    parser.add_argument('--model', type=str, help='使用的模型名称')
    parser.add_argument('--no-markdown', action='store_true', help='不使用Markdown格式')
    parser.add_argument('--list-models', action='store_true', help='列出可用的模型')
    
    args = parser.parse_args()
    
    # 如果需要列出可用模型
    if args.list_models:
        try:
            from openai import OpenAI
            
            # 使用临时API密钥初始化客户端
            temp_api_key = args.api_key
            if not temp_api_key:
                # 尝试从配置文件读取
                config_path = Path(args.config)
                if config_path.exists():
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                            temp_api_key = config.get('api_key')
                    except Exception:
                        pass
            
            if not temp_api_key:
                print("错误：缺少API密钥，无法列出模型")
                return 1
            
            # 初始化客户端
            client = OpenAI(
                api_key=temp_api_key,
                base_url="https://api.siliconflow.cn/v1"
            )
            
            # 列出可用模型
            models = client.models.list()
            
            print("\n可用的模型:")
            print("=" * 60)
            
            # 按类别分组
            categories = {
                "DeepSeek": [],
                "Qwen": [],
                "THUDM": [],
                "Meta": [],
                "其他": []
            }
            
            for model in models.data:
                if "deepseek" in model.id.lower():
                    categories["DeepSeek"].append(model.id)
                elif "qwen" in model.id.lower():
                    categories["Qwen"].append(model.id)
                elif "thudm" in model.id.lower() or "glm" in model.id.lower():
                    categories["THUDM"].append(model.id)
                elif "meta" in model.id.lower() or "llama" in model.id.lower():
                    categories["Meta"].append(model.id)
                else:
                    categories["其他"].append(model.id)
            
            # 打印分组后的模型
            for category, models in categories.items():
                if models:
                    print(f"\n{category}模型:")
                    for model in sorted(models):
                        print(f"  - {model}")
            
            print("\n推荐模型:")
            print("  - Pro/deepseek-ai/DeepSeek-R1 (支持Markdown格式)")
            print("  - Qwen/Qwen2.5-7B-Instruct (备选模型)")
            print("  - THUDM/GLM-4-9B-0414 (备选模型)")
            
            return 0
        except ImportError:
            print("错误：未安装openai库，无法列出模型")
            print("请运行 pip install --upgrade openai 安装")
            return 1
        except Exception as e:
            print(f"列出模型失败: {str(e)}")
            return 1
    
    # 创建配置文件(如果不存在)
    create_config_if_not_exists(args.config, args.api_key)
    
    # 更新配置
    success = update_config(
        args.config,
        api_key=args.api_key,
        use_markdown=not args.no_markdown,
        model=args.model
    )
    
    if success:
        print("\n配置文件更新成功！您的配置已设置为使用siliconflow.cn的DeepSeek API。")
        if not args.no_markdown:
            print("已启用Markdown格式，这将允许Pro/deepseek-ai/DeepSeek-R1模型正常工作。")
        
        # 检查API密钥是否为默认值
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('api_key') in ["YOUR_API_KEY_HERE", ""]:
                    print("\n警告：配置文件中的API密钥未设置！")
                    print("请通过以下方式设置API密钥:")
                    print(f"1. 编辑配置文件：{args.config}")
                    print("2. 重新运行此脚本，使用 --api-key 参数")
        except Exception:
            pass
        
        return 0
    else:
        print("配置文件更新失败！")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main()) 