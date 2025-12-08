#!/usr/bin/env python3
"""
详细调试 codellama 匹配过程
"""

import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig


def debug_codellama_process():
    """详细调试 codellama 匹配过程"""
    print("🔍 详细调试 codellama 匹配过程...")
    
    # 模拟Ollama返回一些可用的模型
    mock_ollama_output = """NAME                            ID               SIZE    MODIFIED
llama3:8b                      abcdef123456     4.7 GB  2 hours ago
mistral:latest                  fedcba654321     4.1 GB  1 day ago
phi3:latest                     123456abcdef     3.8 GB  3 days ago
codellama:7b                    789456123ghi     3.5 GB  4 days ago
"""

    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mock_ollama_output
        mock_run.return_value = mock_result
        
        original_model = "ollama/codellama-new-model"
        print(f"原始模型: {original_model}")
        
        # 手动执行回退逻辑，逐步调试
        if "/" in original_model:
            model_name_part = original_model.split("/", 1)[1].lower()
        else:
            model_name_part = original_model.lower()
        
        print(f"模型名部分: {model_name_part}")
        
        # 检查是否包含 codellama
        if "codellama" in model_name_part:
            print("✅ codellama 关键词在模型名部分中")
        else:
            print("❌ codellama 关键词不在模型名部分中")
        
        # 获取可用模型
        config = ProviderConfig(model="ollama/test")  # 任意配置
        provider = LiteLLMProvider(config)
        available_models = provider._get_available_ollama_models()
        print(f"可用模型: {available_models}")
        
        # 检查每个可用模型是否包含 codellama
        for model in available_models:
            if "codellama" in model.lower():
                print(f"✅ 找到 codellama 模型: {model}")
        
        # 定义匹配函数
        match_func = lambda model: "codellama" in model.lower()
        
        # 逐一检查可用模型
        for model in available_models:
            is_match = match_func(model)
            print(f"  {model} -> 匹配: {is_match}")
            if is_match:
                print(f"  返回匹配模型: {model}")
                return model
        
        # 如果没有找到，返回第一个可用模型
        print(f"  没有找到匹配模型，返回第一个: {available_models[0] if available_models else 'None'}")
        return available_models[0] if available_models else original_model


def test_actual_provider():
    """使用实际的provider类测试"""
    print("\n🔍 使用实际的provider类测试...")
    
    # 模拟Ollama返回一些可用的模型
    mock_ollama_output = """NAME                            ID               SIZE    MODIFIED
llama3:8b                      abcdef123456     4.7 GB  2 hours ago
mistral:latest                  fedcba654321     4.1 GB  1 day ago
phi3:latest                     123456abcdef     3.8 GB  3 days ago
codellama:7b                    789456123ghi     3.5 GB  4 days ago
"""

    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mock_ollama_output
        mock_run.return_value = mock_result
        
        # 直接测试 provider 的方法
        config = ProviderConfig(model="ollama/test")
        provider = LiteLLMProvider(config)
        
        # 使用 force_fallback=True 测试 codellama
        original = "ollama/codellama-new-model"
        result = provider._get_fallback_model(original, force_fallback=True)
        
        print(f"原始模型: {original}")
        print(f"回退结果: {result}")
        print(f"期望结果: ollama/codellama:7b")
        print(f"匹配: {result == 'ollama/codellama:7b'}")


if __name__ == "__main__":
    expected_result = debug_codellama_process()
    print(f"期望返回: {expected_result}")
    test_actual_provider()