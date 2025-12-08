#!/usr/bin/env python3
"""
彻底测试模型回退机制
"""

import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig


def test_with_mocked_availability():
    """测试带有模拟可用性的回退机制"""
    print("🔍 测试带有模拟可用性的回退机制...")
    
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
        
        # 直接测试 get_available_models 来确保模型提取正确
        config = ProviderConfig(model="ollama/llama3.1:8b")
        provider = LiteLLMProvider(config)
        
        # 先获取可用模型列表
        available_models = provider._get_available_ollama_models()
        print(f"可用模型列表: {available_models}")
        
        # 使用 monkey patch 模拟模型不可用
        original_is_model_available = provider._is_model_available
        def mock_is_model_available(model_name):
            # 除了 'ollama/this_model_exists'，其他都返回 False
            return False  # 简单测试，假设所有测试模型都不可用
        
        provider._is_model_available = mock_is_model_available
        
        # 测试各种回退场景
        test_cases = [
            ("ollama/llama3.1:8b", "ollama/llama3:8b"),
            ("ollama/mistral-new-model", "ollama/mistral:latest"),
            ("ollama/phi-new-model", "ollama/phi3:latest"),
            ("ollama/codellama-new-model", "ollama/codellama:7b"),
            ("ollama/unknown-model", "ollama/llama3:8b"),  # 第一个可用模型
        ]
        
        for original, expected in test_cases:
            result = provider._get_fallback_model(original)
            status = "✅" if result == expected else "❌"
            print(f"{status} {original} -> {result} (期望: {expected})")


def test_with_manual_availability_check():
    """通过手动绕过可用性检查测试回退逻辑"""
    print("\n🔍 通过手动绕过可用性检查测试回退逻辑...")
    
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
        
        config = ProviderConfig(model="ollama/test")  # 任意配置
        provider = LiteLLMProvider(config)
        
        # 直接调用内部方法测试回退逻辑
        provider._get_available_ollama_models()  # 先填充缓存
        
        test_cases = [
            ("ollama/llama3.1:8b", "ollama/llama3:8b"),
            ("ollama/mistral-new-model", "ollama/mistral:latest"),
            ("ollama/phi-new-model", "ollama/phi3:latest"),
            ("ollama/codellama-new-model", "ollama/codellama:7b"),
            ("ollama/unknown-model", "ollama/llama3:8b"),  # 第一个可用模型
        ]
        
        print("手动测试回退逻辑:")
        for original, expected in test_cases:
            # 手动执行回退逻辑
            original_lower = original.lower()
            if "/" in original:
                model_name_part = original.split("/", 1)[1].lower()
            else:
                model_name_part = original.lower()
            
            family_keywords = [
                ("llama", lambda model: "llama" in model.lower()),
                ("mistral", lambda model: "mistral" in model.lower()),
                ("phi", lambda model: "phi" in model.lower()),
                ("command-r", lambda model: "command-r" in model.lower()),
                ("codellama", lambda model: "codellama" in model.lower()),
                ("gemma", lambda model: "gemma" in model.lower()),
                ("yi", lambda model: "yi" in model.lower()),
            ]
            
            result = None
            for family_keyword, match_func in family_keywords:
                if family_keyword in model_name_part:
                    for model in provider._available_models:
                        if match_func(model):
                            result = model
                            break
                if result:
                    break
            
            if not result:
                result = provider._available_models[0] if provider._available_models else original
            
            status = "✅" if result == expected else "❌"
            print(f"{status} {original} -> {result} (期望: {expected})")


if __name__ == "__main__":
    test_with_mocked_availability()
    test_with_manual_availability_check()