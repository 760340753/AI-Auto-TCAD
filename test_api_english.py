#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test for DeepSeek API via siliconflow.cn
"""
from openai import OpenAI
import os
import time
from pathlib import Path

# Please replace with your actual API key
API_KEY = "sk-buspthftjrkhcudljfardlbubjlmpfoxehgstdipajrxpccc"

def main():
    print("=" * 60)
    print("Testing DeepSeek API via siliconflow.cn")
    print("=" * 60)
    
    # Check API key
    if API_KEY == "YOUR_API_KEY_HERE":
        print("Error: Please set your API key in the script first")
        return
    
    # Create OpenAI client with timeout
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.siliconflow.cn/v1",
        timeout=30.0  # 30 seconds timeout
    )
    
    # Simple query
    query = "How can we optimize parameters in TCAD simulation to improve SEE resistance? Please list 3 brief suggestions."
    
    print(f"Sending query: {query}")
    print("Calling API, please wait (timeout: 30s)...")
    
    start_time = time.time()
    
    try:
        # Test API availability first
        print("Testing API connection...")
        models_response = client.models.list(timeout=10.0)
        print(f"Available models: {[model.id for model in models_response.data]}")
        
        # Call API with reduced token limit for faster response
        print("Sending chat completion request...")
        response = client.chat.completions.create(
            model="Pro/deepseek-ai/DeepSeek-R1",
            messages=[
                {"role": "system", "content": "You are an expert in semiconductor device physics and radiation effects."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=100,  # Reduced for quicker response
            timeout=30.0
        )
        
        # Calculate response time
        elapsed_time = time.time() - start_time
        
        # Get response
        content = response.choices[0].message.content
        
        print(f"\nResponse received in {elapsed_time:.2f} seconds:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        
        # Save response
        result_dir = Path("./DeepSeek/Responses")
        result_dir.mkdir(parents=True, exist_ok=True)
        
        with open(result_dir / "english_test_response.txt", "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Response saved to: {result_dir / 'english_test_response.txt'}")
        print("API test successful!")
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"API call error after {elapsed_time:.2f} seconds: {type(e).__name__}: {str(e)}")
        
        # More detailed error handling
        if "401" in str(e):
            print("Authentication error: Your API key is invalid")
        elif "404" in str(e):
            print("Not found error: The endpoint or model doesn't exist")
        elif "timeout" in str(e).lower():
            print("Timeout error: The API request took too long to complete")
        elif "connect" in str(e).lower():
            print("Connection error: Could not connect to API server")
        
        print("\nPlease verify:")
        print("1. Your API key is correct")
        print("2. The API endpoint (base_url) is correct")
        print("3. Your network connection is working")
        print("4. The API service is currently available")

if __name__ == "__main__":
    main() 