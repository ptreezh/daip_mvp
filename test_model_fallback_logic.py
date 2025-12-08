#!/usr/bin/env python3
"""
模拟测试模型回退机制，验证代码逻辑
"""

import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig


async def test_model_fallback_logic():
    """测试模型回退机制的逻辑"""
    print("🧪 开始测试模型回退机制逻辑...")
    
    # 创建一个配置，使用一个不存在的模型
    config = ProviderConfig(model="ollama/llama3.1:8b")
    provider = LiteLLMProvider(config)
    
    print(f"📋 原始配置模型: {config.model}")
    
    # 模拟Ollama返回一些可用的模型
    mock_ollama_output = """NAME                            ID               SIZE    MODIFIED
llama3:8b                      abcdef123456     4.7 GB  2 hours ago
mistral:latest                  fedcba654321     4.1 GB  1 day ago
phi3:latest                     123456abcdef     3.8 GB  3 days ago
"""

    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mock_ollama_output
        mock_run.return_value = mock_result
        
        # 测试模型可用性检查
        print("\n🔍 检查模型可用性...")
        is_available = provider._is_model_available(config.model)
        print(f"   模型 {config.model} 可用: {is_available}")
        
        # 获取可用的Ollama模型
        print("\n📋 获取可用的Ollama模型...")
        available_models = provider._get_available_ollama_models()
        print(f"   可用模型数量: {len(available_models)}")
        for model in available_models:
            print(f"   - {model}")
        
        # 获取回退模型
        print(f"\n🔄 获取回退模型...")
        fallback_model = provider._get_fallback_model(config.model)
        print(f"   回退模型: {fallback_model}")
        
        # 验证回退逻辑 - 应该选择一个llama3模型
        expected_fallback = "ollama/llama3:8b"
        print(f"   预期回退模型: {expected_fallback}")
        print(f"   回退逻辑正确: {fallback_model == expected_fallback}")
        
        # 测试获取非llama模型的回退
        mistral_config = ProviderConfig(model="ollama/mistral-new-model") 
        mistral_provider = LiteLLMProvider(mistral_config)
        
        # 设置相同的模拟数据
        mistral_provider._available_models = available_models
        
        print(f"\n🔄 测试Mistral模型回退...")
        mistral_fallback = mistral_provider._get_fallback_model("ollama/mistral-new-model")
        print(f"   Mistral回退模型: {mistral_fallback}")
        expected_mistral = "ollama/mistral:latest"
        print(f"   预期Mistral回退模型: {expected_mistral}")
        print(f"   Mistral回退逻辑正确: {mistral_fallback == expected_mistral}")
    
    print("\n✅ 模型回退机制逻辑测试完成")


def test_error_handling():
    """测试错误处理逻辑"""
    print("\n🛡️ 测试错误处理...")
    
    config = ProviderConfig(model="ollama/llama3.1:8b")
    provider = LiteLLMProvider(config)
    
    # 模拟Ollama未安装或无法运行的情况
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError("ollama command not found")
        
        available_models = provider._get_available_ollama_models()
        print(f"   当Ollama不可用时返回的模型数: {len(available_models)}")
        print(f"   错误处理正确: {available_models == []}")
    
    print("✅ 错误处理测试完成")


if __name__ == "__main__":
    asyncio.run(test_model_fallback_logic())
    test_error_handling()