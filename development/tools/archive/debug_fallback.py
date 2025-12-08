#!/usr/bin/env python3
"""
详细调试模型回退机制
"""

import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig


def debug_fallback_logic():
    """调试回退逻辑"""
    print("🔍 调试回退逻辑...")
    
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
        
        config = ProviderConfig(model="ollama/mistral-something")
        provider = LiteLLMProvider(config)
        
        print(f"原始模型: {config.model}")
        print(f"原始模型小写: {config.model.lower()}")
        
        # 手动检查可用模型
        available_models = provider._get_available_ollama_models()
        print(f"可用模型: {available_models}")
        
        # 提取模型名部分
        if "/" in config.model:
            model_name_part = config.model.split("/", 1)[1].lower()
        else:
            model_name_part = config.model.lower()
        print(f"模型名部分: {model_name_part}")

        family_keywords = [
            ("llama", lambda model: "llama" in model.lower()),
            ("mistral", lambda model: "mistral" in model.lower()),
            ("phi", lambda model: "phi" in model.lower()),
            ("command-r", lambda model: "command-r" in model.lower()),
            ("codellama", lambda model: "codellama" in model.lower()),
            ("gemma", lambda model: "gemma" in model.lower()),
            ("yi", lambda model: "yi" in model.lower()),
        ]

        # 检查是否匹配mistral关键词
        for family_keyword, match_func in family_keywords:
            if family_keyword in model_name_part:
                print(f"匹配到关键词: {family_keyword}")
                for model in available_models:
                    if match_func(model):
                        print(f"找到匹配模型: {model}")
                        return model  # 这是算法会返回的模型
        
        print("没有匹配的模型，将返回第一个可用模型")
        return available_models[0] if available_models else config.model


async def test_with_real_logic():
    """使用真实逻辑测试"""
    print("\n🧪 使用真实逻辑测试...")
    
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
        
        # 测试 mistral-something 的回退
        config = ProviderConfig(model="ollama/mistral-something")
        provider = LiteLLMProvider(config)
        fallback = provider._get_fallback_model(config.model)
        print(f"原始模型: {config.model}")
        print(f"回退模型: {fallback}")
        
        # 测试 phi-something 的回退
        config2 = ProviderConfig(model="ollama/phi-something")
        provider2 = LiteLLMProvider(config2)
        fallback2 = provider2._get_fallback_model(config2.model)
        print(f"原始模型: {config2.model}")
        print(f"回退模型: {fallback2}")
        
        # 测试 codellama-something 的回退
        config3 = ProviderConfig(model="ollama/codellama-something")
        provider3 = LiteLLMProvider(config3)
        fallback3 = provider3._get_fallback_model(config3.model)
        print(f"原始模型: {config3.model}")
        print(f"回退模型: {fallback3}")


if __name__ == "__main__":
    result = debug_fallback_logic()
    print(f"手动检查返回模型: {result}")
    asyncio.run(test_with_real_logic())