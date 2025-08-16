#!/usr/bin/env python3
"""验证LLM集成服务
"""

import asyncio
import sys

sys.path.append('src')

def test_llm_integration_service():
    """测试LLM集成服务"""
    try:
        from src.real_demo_system.llm_integration_service import LLMBackend, LLMIntegrationService

        # 创建服务
        service = LLMIntegrationService()

        # 验证基本属性
        assert hasattr(service, 'available_models'), "缺少available_models属性"
        assert hasattr(service, 'call_history'), "缺少call_history属性"

        # 验证基本方法
        assert hasattr(service, 'get_available_models'), "缺少get_available_models方法"
        assert hasattr(service, 'generate'), "缺少generate方法"
        assert callable(service.generate), "generate不可调用"

        # 验证模型获取
        models = service.get_available_models()
        assert isinstance(models, dict), "models应为字典"
        assert LLMBackend.OLLAMA in models, "应包含OLLAMA后端"

        print("✅ LLMIntegrationService验证通过")
        return True

    except Exception as e:
        print(f"❌ LLMIntegrationService验证失败: {e}")
        return False

async def test_llm_generate():
    """测试LLM生成功能"""
    try:
        from src.real_demo_system.llm_integration_service import LLMBackend, LLMIntegrationService

        service = LLMIntegrationService()

        # 测试生成功能
        response = await service.generate(
            prompt="测试提示：请简单回答'测试成功'",
            backend=LLMBackend.OLLAMA,
            temperature=0.1,
            max_tokens=50
        )

        # 验证响应
        assert hasattr(response, 'content'), "响应缺少content属性"
        assert hasattr(response, 'call_record'), "响应缺少call_record属性"
        assert len(response.content) > 0, "响应内容为空"

        print("✅ LLM生成功能验证通过")
        return True

    except Exception as e:
        print(f"❌ LLM生成功能验证失败: {e}")
        return False

def test_llm_config():
    """测试LLM配置"""
    try:
        from src.kernel.llm_interface import LLMConfig

        # 创建配置
        config = LLMConfig(
            provider="ollama",
            model="gemma3:latest",
            base_url="http://localhost:11434",
            temperature=0.3,
            max_tokens=2048
        )

        # 验证配置
        assert config.provider == "ollama", "provider不匹配"
        assert config.model == "gemma3:latest", "model不匹配"
        assert config.temperature == 0.3, "temperature不匹配"
        assert config.max_tokens == 2048, "max_tokens不匹配"

        print("✅ LLM配置验证通过")
        return True

    except Exception as e:
        print(f"❌ LLM配置验证失败: {e}")
        return False

async def main():
    """主验证函数"""
    print("🚀 开始验证LLM集成服务")

    tests = [
        ("LLMIntegrationService", test_llm_integration_service),
        ("LLMConfig", test_llm_config),
        ("LLM生成功能", test_llm_generate)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 验证 {test_name}...")
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()

        if result:
            passed += 1
        else:
            print(f"❌ {test_name} 验证失败，停止后续测试")
            break

    if passed == total:
        print(f"\n✅ 所有验证通过 ({passed}/{total})")
        return True
    else:
        print(f"\n❌ 验证失败 ({passed}/{total})")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
