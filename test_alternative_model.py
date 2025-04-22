#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testing alternative models via siliconflow.cn
"""
from openai import OpenAI
import os
import time
import json
from pathlib import Path

# Please replace with your actual API key
API_KEY = "sk-buspthftjrkhcudljfardlbubjlmpfoxehgstdipajrxpccc"

def test_model(client, model_name, query):
    """Test a specific model"""
    print(f"\n\nTesting model: {model_name}")
    print("-" * 60)
    
    try:
        start_time = time.time()
        print(f"Sending request to {model_name}...")
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=100,
            timeout=30.0
        )
        
        elapsed_time = time.time() - start_time
        
        # Get response
        content = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
        
        print(f"Response received in {elapsed_time:.2f} seconds")
        print(f"Finish reason: {finish_reason}")
        
        print("\nResponse content:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        
        # Save response
        result_dir = Path(f"./DeepSeek/AlternativeModels/{model_name.replace('/', '_')}")
        result_dir.mkdir(parents=True, exist_ok=True)
        
        with open(result_dir / "response.txt", "w", encoding="utf-8") as f:
            f.write(content)
        
        return True, content
        
    except Exception as e:
        print(f"Error testing model {model_name}: {type(e).__name__}: {str(e)}")
        return False, str(e)

def main():
    print("=" * 60)
    print("Testing Alternative Models via siliconflow.cn")
    print("=" * 60)
    
    # Create results directory
    results_dir = Path("./DeepSeek/AlternativeModels")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Create OpenAI client
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.siliconflow.cn/v1",
        timeout=30.0
    )
    
    # List available models first
    print("Fetching available models...")
    try:
        models_response = client.models.list(timeout=10.0)
        available_models = [model.id for model in models_response.data]
        print(f"Found {len(available_models)} available models")
        
        # Save model list
        with open(results_dir / "available_models.json", "w", encoding="utf-8") as f:
            json.dump(available_models, f, indent=2)
        
    except Exception as e:
        print(f"Error listing models: {type(e).__name__}: {str(e)}")
        available_models = []
    
    # Models to test
    test_models = [
        # DeepSeek models
        "deepseek-ai/DeepSeek-R1",             # Non-Pro version
        "Pro/deepseek-ai/DeepSeek-R1",         # Pro version (the one we tried)
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",  # Distilled version
        
        # Other models that might work
        "Qwen/Qwen2.5-7B-Instruct",          # Qwen model
        "THUDM/GLM-4-9B-0414",               # GLM model
        "Pro/Qwen/Qwen2-7B-Instruct"         # Pro Qwen model
    ]
    
    # The query
    query = "How can we optimize parameters in TCAD simulation to improve SEE resistance? List 2 brief suggestions."
    
    # Test each model
    results = {}
    for model in test_models:
        if model in available_models:
            success, response = test_model(client, model, query)
            results[model] = {
                "success": success,
                "response": response if success else None,
                "error": None if success else response
            }
        else:
            print(f"\n\nModel {model} not available, skipping...")
            results[model] = {
                "success": False,
                "response": None,
                "error": "Model not available"
            }
    
    # Summary
    print("\n\n" + "=" * 60)
    print("SUMMARY OF RESULTS")
    print("=" * 60)
    
    for model, result in results.items():
        status = "SUCCESS" if result["success"] else "FAILED"
        print(f"{model}: {status}")
        if not result["success"]:
            print(f"  Error: {result['error']}")
    
    # Save results
    with open(results_dir / "test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_dir / 'test_results.json'}")

if __name__ == "__main__":
    main() 