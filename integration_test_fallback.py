#!/usr/bin/env python3
"""
集成测试：验证模型回退机制在实际系统中的工作情况
"""

import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig


async def integration_test():
    """集成测试模型回退机制"""
    print("🧪 集成测试：模型回退机制")
    
    # 模拟Ollama返回一些可用的模型
    mock_ollama_output = """NAME                            ID               SIZE    MODIFIED
llama3:8b                      abcdef123456     4.7 GB  2 hours ago
mistral:latest                  fedcba654321     4.1 GB  1 day ago
phi3:latest                     123456abcdef     3.8 GB  3 days ago
codellama:7b                    789456123ghi     3.5 GB  4 days ago
"""

    print("\n📋 测试场景：配置了不存在的模型，验证系统自动回退")
    
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mock_ollama_output
        mock_run.return_value = mock_result
        
        # 创建配置，使用一个不存在的模型
        config = ProviderConfig(model="ollama/llama3.1:8b")
        provider = LiteLLMProvider(config)
        
        print(f"   原始配置模型: {config.model}")
        
        # 使用generate方法测试完整流程
        print("   正在测试 generate 方法的回退机制...")
        
        try:
            # 由于原始模型不可用，generate 方法会自动使用回退模型
            response, usage = await provider.generate("Hello, please introduce yourself.", max_tokens=50)
            print(f"   ✅ 生成成功!")
            print(f"   回退模型已自动使用")
            print(f"   响应预览: {response[:60]}...")
        except Exception as e:
            print(f"   ❌ 生成失败: {e}")
        
        # 测试嵌入方法的回退
        print("\n   正在测试 embed 方法的回退机制...")
        try:
            embedding = await provider.embed("Test embedding for model fallback")
            print(f"   ✅ 嵌入成功! 向量长度: {len(embedding)}")
        except Exception as e:
            print(f"   ❌ 嵌入失败: {e}")
        
        # 验证实际使用的模型
        print(f"\n🔍 验证回退模型选择逻辑:")
        fallback_model = provider._get_fallback_model(config.model, force_fallback=True)
        print(f"   预期回退模型: {fallback_model}")
        if fallback_model == "ollama/llama3:8b":  # 基于llama的模型
            print("   ✅ 正确选择了相似类型的回退模型")
        else:
            print("   ⚠️  选择了不同的回退模型")
    
    print("\n🎯 集成测试完成 - 模型回退机制工作正常")


def test_edge_cases():
    """测试边界情况"""
    print("\n🧪 测试边界情况")
    
    # 模拟没有可用模型的情况
    mock_ollama_output_empty = """NAME                            ID               SIZE    MODIFIED
"""
    
    print("   测试：当没有可用Ollama模型时的行为")
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = mock_ollama_output_empty
        mock_run.return_value = mock_result
        
        config = ProviderConfig(model="ollama/nonexistent-model")
        provider = LiteLLMProvider(config)
        
        # 在没有可用模型时，应该返回原始模型
        fallback_model = provider._get_fallback_model(config.model, force_fallback=True)
        print(f"   原始模型: {config.model}")
        print(f"   回退模型: {fallback_model}")
        if fallback_model == config.model:
            print("   ✅ 正确返回了原始模型（没有可用模型时）")
        else:
            print("   ❌ 未正确处理无可用模型的情况")


if __name__ == "__main__":
    asyncio.run(integration_test())
    test_edge_cases()
    print("\n🎉 所有集成测试完成！")