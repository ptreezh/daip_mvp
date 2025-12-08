#!/usr/bin/env python3
"""
最终测试模型回退机制 - 使用force_fallback参数
"""

import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig


def test_fallback_with_force():
    """测试强制回退功能"""
    print("🔍 测试强制回退功能...")
    
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
        
        test_cases = [
            ("ollama/llama3.1:8b", "ollama/llama3:8b"),
            ("ollama/mistral-new-model", "ollama/mistral:latest"),
            ("ollama/phi-new-model", "ollama/phi3:latest"),
            ("ollama/codellama-new-model", "ollama/codellama:7b"),
            ("ollama/unknown-model", "ollama/llama3:8b"),  # 第一个可用模型
        ]
        
        print("使用force_fallback=True测试:")
        for original, expected in test_cases:
            result = provider._get_fallback_model(original, force_fallback=True)
            status = "✅" if result == expected else "❌"
            print(f"{status} {original} -> {result} (期望: {expected})")
    
    print("\n✅ 所有测试完成")


if __name__ == "__main__":
    test_fallback_with_force()