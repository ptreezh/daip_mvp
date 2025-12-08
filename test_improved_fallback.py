#!/usr/bin/env python3
"""
测试改进后的模型回退机制
"""

import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig


async def test_improved_fallback_logic():
    """测试改进后的模型回退机制逻辑"""
    print("🧪 开始测试改进后的模型回退机制逻辑...")
    
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
        
        # 测试 llama3.1:8b 的回退（应该选择 llama3:8b）
        print("\n🔍 测试 llama3.1:8b 的回退...")
        config1 = ProviderConfig(model="ollama/llama3.1:8b")
        provider1 = LiteLLMProvider(config1)
        fallback1 = provider1._get_fallback_model(config1.model)
        print(f"   原始模型: {config1.model}")
        print(f"   回退模型: {fallback1}")
        print(f"   预期模型: ollama/llama3:8b")
        print(f"   正确: {fallback1 == 'ollama/llama3:8b'}")
        
        # 测试 mistral-new-model 的回退（应该选择 mistral:latest）
        print("\n🔍 测试 mistral-new-model 的回退...")
        config2 = ProviderConfig(model="ollama/mistral-new-model")
        provider2 = LiteLLMProvider(config2)
        fallback2 = provider2._get_fallback_model(config2.model)
        print(f"   原始模型: {config2.model}")
        print(f"   回退模型: {fallback2}")
        print(f"   预期模型: ollama/mistral:latest")
        print(f"   正确: {fallback2 == 'ollama/mistral:latest'}")
        
        # 测试 phi-new-model 的回退（应该选择 phi3:latest）
        print("\n🔍 测试 phi-new-model 的回退...")
        config3 = ProviderConfig(model="ollama/phi-new-model")
        provider3 = LiteLLMProvider(config3)
        fallback3 = provider3._get_fallback_model(config3.model)
        print(f"   原始模型: {config3.model}")
        print(f"   回退模型: {fallback3}")
        print(f"   预期模型: ollama/phi3:latest")
        print(f"   正确: {fallback3 == 'ollama/phi3:latest'}")
        
        # 测试一个完全不匹配的模型（应该选择第一个可用的）
        print("\n🔍 测试不匹配模型的回退...")
        config4 = ProviderConfig(model="ollama/nonexistent-model")
        provider4 = LiteLLMProvider(config4)
        fallback4 = provider4._get_fallback_model(config4.model)
        print(f"   原始模型: {config4.model}")
        print(f"   回退模型: {fallback4}")
        print(f"   预期模型: ollama/llama3:8b (第一个可用的)")
        print(f"   正确: {fallback4 == 'ollama/llama3:8b'}")
        
        # 测试 codellama 相关模型的回退（应该选择 codellama:7b）
        print("\n🔍 测试 codellama 相关模型的回退...")
        config5 = ProviderConfig(model="ollama/codellama-python")
        provider5 = LiteLLMProvider(config5)
        fallback5 = provider5._get_fallback_model(config5.model)
        print(f"   原始模型: {config5.model}")
        print(f"   回退模型: {fallback5}")
        print(f"   预期包含: codellama")
        print(f"   正确: {'codellama' in fallback5.lower()}")
    
    print("\n✅ 改进后的模型回退机制逻辑测试完成")


if __name__ == "__main__":
    asyncio.run(test_improved_fallback_logic())