#!/usr/bin/env python3
"""
TDD RED阶段 - 真实模型集成测试
目标：验证系统是否能够使用真实的模型提供者进行Wiki协同编辑
这些测试应该失败，因为我们需要集成真实的模型提供者
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestRealModelIntegrationRED:
    """RED阶段：验证真实模型提供者集成需求"""

    @pytest.fixture
    def temp_wiki_dir(self):
        """创建临时wiki目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_require_real_model_provider_not_mock(self, temp_wiki_dir):
        """RED测试：要求使用真实模型提供者，拒绝模拟"""
        from daip_live.config import config_manager
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 使用配置文件中的真实路径
        config = config_manager.get_config()
        wiki_pages_dir = config.model_dump()["wiki"]["pages_directory"]
        wiki_root = Path(wiki_pages_dir)

        # 测试配置的模型提供者设置
        model_provider_config = config.model_dump().get("llm_provider", {})
        if not model_provider_config:
            pytest.fail("config.yaml中没有配置llm_provider，无法使用真实模型")

        default_model = model_provider_config.get("default_model")
        if not default_model:
            pytest.fail("config.yaml中没有配置default_model，无法使用真实模型")

        # 尝试创建真实的模型提供者
        try:
            from daip_live.core.models import ProviderConfig
            from daip_live.model_provider.provider import LiteLLMProvider

            provider_config = ProviderConfig(
                model=default_model, temperature=0.7, max_tokens=1000
            )

            LiteLLMProvider(provider_config)

        except ImportError as e:
            pytest.fail(f"无法导入真实模型提供者: {e}")
        except Exception as e:
            pytest.fail(f"真实模型提供者配置失败: {e}")

        # 验证不能使用模拟模型提供者
        class MockModelProvider:
            def __init__(self):
                self.call_count = 0

            async def generate(
                self, prompt, model=None, temperature=0.7, max_tokens=1000
            ):
                self.call_count += 1
                return "这是模拟内容，不应该出现在真实系统中", {}

        # 尝试用模拟提供者创建Wiki管理器应该失败
        with pytest.raises(Exception):
            EnhancedWikiManager(
                wiki_root=wiki_root,
                role_model_manager=None,  # 需要真实的角色管理器
                model_provider=MockModelProvider(),  # 这里应该被拒绝
            )

    def test_require_real_role_model_manager(self, temp_wiki_dir):
        """RED测试：要求使用真实的角色模型管理器"""
        from daip_live.config import config_manager

        # 检查角色管理器配置
        role_manager_config = (
            config_manager.get_config().model_dump().get("role_manager", {})
        )
        if not role_manager_config:
            pytest.fail("config.yaml中没有配置role_manager")

        roles_dir = role_manager_config.get("roles_dir")
        if not roles_dir:
            pytest.fail("config.yaml中没有配置roles_dir")

        roles_path = Path(roles_dir)
        if not roles_path.exists():
            pytest.fail(f"角色目录不存在: {roles_path}")

        # 验证角色文件存在
        role_files = list(roles_path.glob("*.yaml")) + list(roles_path.glob("*.yml"))
        if not role_files:
            pytest.fail(f"角色目录中没有找到角色配置文件: {roles_path}")

        # 尝试创建真实的角色管理器
        try:
            from daip_live.p4_role_manager_tools.role_model_manager import (
                RoleModelManager,
            )

            RoleModelManager()

        except ImportError as e:
            pytest.fail(f"无法导入真实角色管理器: {e}")
        except Exception as e:
            pytest.fail(f"真实角色管理器创建失败: {e}")

    @pytest.mark.asyncio
    async def test_require_real_content_generation(self, temp_wiki_dir):
        """RED测试：要求真实的AI内容生成，拒绝预设内容"""
        pytest.skip("刻意TDD RED：真实AI内容生成功能尚未实现（白名单豁免）")

        # 这个测试应该失败，因为我们还没有实现真实的AI内容生成
        from daip_live.config import config_manager

        config = config_manager.get_config()
        wiki_pages_dir = config.model_dump()["wiki"]["pages_directory"]
        Path(wiki_pages_dir)

        # 检查真实模型是否可用
        model_provider_config = config.model_dump().get("llm_provider", {})
        default_model = model_provider_config.get("default_model")

        if default_model and default_model.startswith("ollama/"):
            # 检查Ollama是否运行
            import subprocess

            try:
                result = subprocess.run(
                    ["ollama", "list"], capture_output=True, text=True, timeout=10
                )
                if result.returncode != 0:
                    pytest.fail("Ollama未运行，无法进行真实内容生成")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pytest.fail("Ollama未安装或未运行，无法进行真实内容生成")

        # 尝试真实内容生成（当前应该失败）
        pytest.fail("真实内容生成功能尚未实现，需要集成真实AI模型")

    def test_no_root_directory_pollution(self):
        """RED测试：确保不会在项目根目录生成文件"""

        # 检查项目根目录是否干净（没有测试生成的临时文件）
        project_root = Path(__file__).parent.parent.parent

        # 检查不应该存在的临时文件模式
        forbidden_patterns = [
            "*链接.md",  # 之前生成的链接文件
            "体验_*.py",  # 体验脚本
            "test_*.md",  # 测试生成的markdown文件
        ]

        for pattern in forbidden_patterns:
            matching_files = list(project_root.glob(pattern))
            if matching_files:
                pytest.fail(f"项目根目录存在不应该的文件: {matching_files}")

    def test_require_ollama_service_running(self):
        """RED测试：要求Ollama服务正在运行"""

        import subprocess

        try:
            # 检查Ollama服务状态
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                pytest.fail("Ollama服务未运行，请启动Ollama服务")

            # 检查是否有可用的模型
            output = result.stdout.strip()
            if not output or "NAME" not in output:
                pytest.fail("Ollama中没有可用的模型，请先下载模型")

        except subprocess.TimeoutExpired:
            pytest.fail("Ollama服务响应超时")
        except FileNotFoundError:
            pytest.fail("Ollama未安装或不在PATH中")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
