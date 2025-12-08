#!/usr/bin/env python3
"""
单独测试codellama的匹配
"""

import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig


async def test_codellama():
    """测试codellama匹配"""
    print("🔍 测试codellama匹配...")
    
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
        
        # 详细分析 codellama 匹配
        config = ProviderConfig(model="ollama/codellama-python")
        provider = LiteLLMProvider(config)
        
        print(f"原始模型: {config.model}")
        
        # 提取模型名部分
        if "/" in config.model:
            model_name_part = config.model.split("/", 1)[1].lower()
        else:
            model_name_part = config.model.lower()
        print(f"模型名部分: {model_name_part}")
        
        # 检查可用模型
        available_models = provider._get_available_ollama_models()
        print(f"可用模型: {available_models}")
        
        # 检查 codellama 关键词是否匹配
        if "codellama" in model_name_part:
            print("✅ codellama 关键词匹配成功")
            for model in available_models:
                if "codellama" in model.lower():
                    print(f"✅ 找到匹配的codellama模型: {model}")
        else:
            print("❌ codellama 关键词没有匹配")
        
        # 测试回退结果
        fallback = provider._get_fallback_model(config.model)
        print(f"回退模型: {fallback}")
        print(f"预期: ollama/codellama:7b")
        print(f"匹配: {fallback == 'ollama/codellama:7b'}")


if __name__ == "__main__":
    asyncio.run(test_codellama())