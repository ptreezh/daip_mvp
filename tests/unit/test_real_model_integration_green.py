#!/usr/bin/env python3
"""
TDD GREEN阶段 - 真实模型集成测试
目标：最小化实现真实模型提供者和角色管理器集成，让测试通过
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class TestRealModelIntegrationGREEN:
    """GREEN阶段：实现真实模型集成的最小功能"""

    @pytest.fixture
    def temp_wiki_dir(self):
        """创建临时wiki目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_create_real_model_provider(self):
        """GREEN测试：创建真实的模型提供者"""
        from daip_live.model_provider.provider import LiteLLMProvider
        from daip_live.core.models import ProviderConfig
        from daip_live.config import config_manager

        # 从配置读取模型设置
        config = config_manager.get_config()
        model_config = config.model_dump().get('llm_provider', {})
        default_model = model_config.get('default_model', 'ollama/llama3')

        # 创建真实的模型提供者
        provider_config = ProviderConfig(
            model=default_model,
            temperature=0.7,
            max_tokens=1000
        )

        real_provider = LiteLLMProvider(provider_config)

        # 验证是真实的模型提供者
        assert isinstance(real_provider, LiteLLMProvider)
        assert hasattr(real_provider, 'config')
        assert real_provider.config.model == default_model

        print(f"✅ 成功创建真实模型提供者: {default_model}")

        return real_provider

    def test_create_real_role_manager(self):
        """GREEN测试：创建真实的角色管理器"""
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager

        # 使用配置中的角色目录
        role_manager = RoleModelManager()

        # 验证是真实的角色管理器
        assert isinstance(role_manager, RoleModelManager)

        # 验证有角色配置
        available_roles = list(role_manager._roles.keys())
        assert len(available_roles) > 0

        print(f"✅ 成功创建真实角色管理器，可用角色: {available_roles}")

        return role_manager

    def test_enhanced_wiki_manager_accepts_real_components(self, temp_wiki_dir):
        """GREEN测试：EnhancedWikiManager接受真实组件"""
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        real_provider = self.test_create_real_model_provider()
        real_role_manager = self.test_create_real_role_manager()

        # 应该成功接受真实组件
        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            role_model_manager=real_role_manager,
            model_provider=real_provider
        )

        assert enhanced_wiki is not None
        assert enhanced_wiki.simple_collaboration_engine is not None

        print("✅ EnhancedWikiManager成功接受真实组件")

        return enhanced_wiki

    def test_enhanced_wiki_manager_rejects_mock_provider(self, temp_wiki_dir):
        """GREEN测试：EnhancedWikiManager拒绝模拟提供者"""
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        class MockModelProvider:
            def __init__(self):
                self.call_count = 0

            async def generate(self, prompt, model=None, temperature=0.7, max_tokens=1000):
                self.call_count += 1
                return "模拟内容", {}

        # 应该拒绝模拟提供者
        with pytest.raises(ValueError) as exc_info:
            EnhancedWikiManager(
                wiki_root=temp_wiki_dir,
                model_provider=MockModelProvider()
            )

        assert "必须使用真实的LiteLLMProvider" in str(exc_info.value)
        print(f"✅ 正确拒绝模拟提供者: {exc_info.value}")

    def test_enhanced_wiki_manager_rejects_mock_role_manager(self, temp_wiki_dir):
        """GREEN测试：EnhancedWikiManager拒绝模拟角色管理器"""
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        class MockRoleManager:
            def get_role_model_mapping(self, role_name):
                return None

        # 应该拒绝模拟角色管理器
        with pytest.raises(ValueError) as exc_info:
            EnhancedWikiManager(
                wiki_root=temp_wiki_dir,
                role_model_manager=MockRoleManager()
            )

        assert "必须使用真实的RoleModelManager" in str(exc_info.value)
        print(f"✅ 正确拒绝模拟角色管理器: {exc_info.value}")

    @pytest.mark.asyncio
    async def test_real_model_generation_minimal(self):
        """GREEN测试：最小化真实模型生成测试"""
        from daip_live.model_provider.provider import LiteLLMProvider
        from daip_live.core.models import ProviderConfig
        from daip_live.config import config_manager

        # 检查Ollama是否可用
        import subprocess
        try:
            result = subprocess.run(['ollama', 'list'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                pytest.skip("Ollama未运行，跳过真实模型测试")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Ollama未安装或未运行，跳过真实模型测试")

        # 创建真实模型提供者
        config = config_manager.get_config()
        model_config = config.model_dump().get('llm_provider', {})
        default_model = model_config.get('default_model', 'ollama/llama3')

        provider_config = ProviderConfig(
            model=default_model,
            temperature=0.7,
            max_tokens=100
        )

        real_provider = LiteLLMProvider(provider_config)

        # 尝试真实生成（最小测试）
        try:
            result = await real_provider.agenerate(
                prompt="请用一句话回答：什么是人工智能？",
                temperature=0.7,
                max_tokens=100
            )

            # 验证返回结果
            assert result is not None
            assert len(result) == 2  # 应该返回 (content, metadata)

            content, metadata = result
            assert isinstance(content, str)
            assert len(content.strip()) > 0
            assert isinstance(metadata, dict)

            print(f"✅ 真实模型生成成功，内容长度: {len(content)}")
            print(f"   内容预览: {content[:50]}...")

        except Exception as e:
            pytest.fail(f"真实模型生成失败: {e}")

    @pytest.mark.asyncio
    async def test_simple_real_wiki_creation(self, temp_wiki_dir):
        """GREEN测试：简单真实Wiki创建测试"""
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 获取真实组件
        real_provider = self.test_create_real_model_provider()
        real_role_manager = self.test_create_real_role_manager()

        # 创建EnhancedWikiManager
        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            role_model_manager=real_role_manager,
            model_provider=real_provider
        )

        # 验证可以创建基础Wiki页面（不使用协作功能）
        basic_page = enhanced_wiki.create_page(
            title="测试页面",
            content="这是一个基础测试页面内容。",
            tags=["测试", "基础"]
        )

        assert basic_page is not None
        assert basic_page.title == "测试页面"
        assert basic_page.content == "这是一个基础测试页面内容。"
        assert "测试" in basic_page.tags
        assert basic_page.file_path.exists()

        print(f"✅ 基础Wiki页面创建成功: {basic_page.file_path}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])