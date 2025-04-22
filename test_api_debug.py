#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug version of DeepSeek API test via siliconflow.cn
"""
from openai import OpenAI
import os
import time
import json
from pathlib import Path

# Please replace with your actual API key
API_KEY = "sk-buspthftjrkhcudljfardlbubjlmpfoxehgstdipajrxpccc"

def main():
    print("=" * 60)
    print("Debug Testing DeepSeek API via siliconflow.cn")
    print("=" * 60)
    
    # Create debug log directory
    debug_dir = Path("./DeepSeek/Debug")
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a log file
    log_file = debug_dir / "api_debug_log.txt"
    
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("API Debug Test Log\n")
        log.write("=" * 60 + "\n")
        log.write(f"API Key (masked): {API_KEY[:5]}...{API_KEY[-5:]}\n")
        log.write(f"Test started at: {time.ctime()}\n\n")
        
        # Create OpenAI client
        try:
            log.write("Creating OpenAI client...\n")
            client = OpenAI(
                api_key=API_KEY,
                base_url="https://api.siliconflow.cn/v1",
                timeout=60.0
            )
            log.write("Client created successfully\n")
            
            # Test connection
            log.write("\nTesting API connection...\n")
            try:
                models_response = client.models.list(timeout=20.0)
                model_ids = [model.id for model in models_response.data]
                log.write(f"Available models: {json.dumps(model_ids, indent=2)}\n")
                print(f"Found {len(model_ids)} available models")
                
                # Check if our target model is available
                target_model = "Pro/deepseek-ai/DeepSeek-R1"
                if target_model in model_ids:
                    log.write(f"\nTarget model '{target_model}' is available\n")
                    print(f"Target model '{target_model}' is available")
                else:
                    log.write(f"\nWARNING: Target model '{target_model}' not found in available models\n")
                    print(f"WARNING: Target model '{target_model}' not found in available models")
                    
            except Exception as e:
                log.write(f"Error listing models: {type(e).__name__}: {str(e)}\n")
                print(f"Error listing models: {type(e).__name__}: {str(e)}")
            
            # Test chat completion
            log.write("\nTesting chat completion...\n")
            query = "How can we optimize parameters in TCAD simulation to improve SEE resistance? List 2 brief suggestions."
            log.write(f"Query: {query}\n")
            print(f"Query: {query}")
            
            try:
                start_time = time.time()
                log.write(f"Sending request at: {time.ctime()}\n")
                
                messages = [
                    {"role": "system", "content": "You are an expert in semiconductor device physics and radiation effects."},
                    {"role": "user", "content": query}
                ]
                log.write(f"Messages: {json.dumps(messages, indent=2)}\n")
                
                response = client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=100,
                    timeout=60.0
                )
                
                elapsed_time = time.time() - start_time
                log.write(f"Response received after {elapsed_time:.2f} seconds\n")
                print(f"Response received after {elapsed_time:.2f} seconds")
                
                # Log full response object details
                response_dict = {
                    "id": response.id,
                    "created": response.created,
                    "model": response.model,
                    "choices": [{
                        "index": c.index,
                        "finish_reason": c.finish_reason,
                        "message": {
                            "role": c.message.role,
                            "content": c.message.content
                        }
                    } for c in response.choices]
                }
                
                log.write(f"Response object: {json.dumps(response_dict, indent=2)}\n")
                
                # Extract content
                content = response.choices[0].message.content
                log.write(f"\nContent from response:\n{content}\n")
                
                # Output content to console
                print("\nResponse content:")
                print("-" * 60)
                print(content)
                print("-" * 60)
                
                # Save response to file
                response_file = debug_dir / "api_response.txt"
                with open(response_file, "w", encoding="utf-8") as f:
                    f.write(content)
                log.write(f"Response saved to: {response_file}\n")
                print(f"Response saved to: {response_file}")
                
                # Check if content is empty
                if not content.strip():
                    log.write("WARNING: Response content is empty!\n")
                    print("WARNING: Response content is empty!")
                
            except Exception as e:
                elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
                log.write(f"Error in chat completion after {elapsed_time:.2f} seconds: {type(e).__name__}: {str(e)}\n")
                print(f"Error in chat completion: {type(e).__name__}: {str(e)}")
            
        except Exception as e:
            log.write(f"Error creating client: {type(e).__name__}: {str(e)}\n")
            print(f"Error creating client: {type(e).__name__}: {str(e)}")
        
        log.write(f"\nTest completed at: {time.ctime()}\n")
        print(f"\nDebug test completed. Log saved to: {log_file}")
    
    # Print additional help
    print("\nIf you're still having issues, please check:")
    print("1. The API key is correct")
    print("2. Network connectivity to api.siliconflow.cn")
    print("3. The model 'Pro/deepseek-ai/DeepSeek-R1' is available")
    print("4. Your account has access to the requested model")

if __name__ == "__main__":
    main() 