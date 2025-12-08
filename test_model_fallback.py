#!/usr/bin/env python3
"""
测试模型回退机制
验证当配置的模型不存在时，系统是否能够自动回退到可用模型
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig


async def test_model_fallback():
    """测试模型回退机制"""
    print("🧪 开始测试模型回退机制...")
    
    # 创建一个配置，使用一个可能不存在的模型
    config = ProviderConfig(model="ollama/llama3.1:8b")
    provider = LiteLLMProvider(config)
    
    print(f"📋 原始配置模型: {config.model}")
    
    # 测试模型可用性检查
    print("\n🔍 检查模型可用性...")
    is_available = provider._is_model_available(config.model)
    print(f"   模型 {config.model} 可用: {is_available}")
    
    # 获取可用的Ollama模型
    print("\n📋 获取可用的Ollama模型...")
    available_models = provider._get_available_ollama_models()
    print(f"   可用模型数量: {len(available_models)}")
    for model in available_models[:5]:  # 只显示前5个
        print(f"   - {model}")
    if len(available_models) > 5:
        print(f"   ... 还有 {len(available_models) - 5} 个模型")
    
    # 获取回退模型
    print(f"\n🔄 获取回退模型...")
    fallback_model = provider._get_fallback_model(config.model)
    print(f"   回退模型: {fallback_model}")
    
    # 如果有可用模型，尝试生成内容
    if available_models:
        print(f"\n📝 测试使用回退模型生成内容...")
        try:
            response, usage = await provider.generate("Hello, world! What is AI?", max_tokens=50)
            print(f"   ✅ 生成成功!")
            print(f"   响应: {response[:100]}...")
            print(f"   使用情况: {usage}")
        except Exception as e:
            print(f"   ❌ 生成失败: {e}")
    else:
        print(f"\n⚠️  没有可用的Ollama模型，请先运行 'ollama pull' 命令下载模型")
    
    print("\n✅ 模型回退机制测试完成")


if __name__ == "__main__":
    asyncio.run(test_model_fallback())