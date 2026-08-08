#!/usr/bin/env python3
"""
TDD RED阶段测试（重写）- 多模型Wiki协作

按真实生产契约对齐（与 green 同源，覆盖不同角度）：
- 不再用 Mock 臆想接口（旧版 MultiRoleWikiCollaborator + Mock 走
  EnhancedDebateManager 真实校验，生产代码对 Mock 返回值 len() 抛
  TypeError —— 断言的是假象而非契约）
- 重定 3 个 RED 断言：
  1. 多角色协作使用不同模型 -> 真实 RoleModelManager + YAML 的角色->模型映射差异
     （get_role_model_mapping / get_debate_model_mappings 契约）
  2. EnhancedWikiManager 协作方法 -> 真实依赖组装（真实 RoleModelManager +
     真实 LiteLLMProvider 实例，仅替换实例 generate 为确定性 async 实现）
  3. 内容合成质量 -> EnhancedWikiManager 高层路径的章节/贡献/协作标识断言
- 新增：CollaborationProgress 时间戳契约、WikiManager 真实异常路径

契约来源（实测于源码）：
- RoleModelMapping.role_name / role_model_config（role_model_config.py:113-114）
- get_debate_model_mappings 保持 1:1，未知角色返回 None 占位
  （role_model_manager.py:87-93）
- WikiManager: 非 Path 根 TypeError("wiki_root must be a Path object")；
  create_page 重复非空 ValueError("...already exists and contains content...")；
  空标题 ValueError("Title cannot be empty")；
  update_page 不存在 ValueError("Page with title '...' not found")
- EnhancedWikiManager 硬性校验 isinstance(LiteLLMProvider)
  /isinstance(RoleModelManager)，依赖齐备时组装 SimpleCollaborationEngine
  （collaborative_wiki.py:221-260）
"""
import asyncio
import textwrap
from datetime import datetime
from unittest.mock import Mock

import pytest

from daip_live.core.models import ProviderConfig
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.wiki.collaborative_wiki import EnhancedWikiManager
from daip_live.wiki.manager import WikiManager
from daip_live.wiki.simple_collaboration_engine import CollaborationProgress

ROLE_YAML = textwrap.dedent(
    """\
    persona: 领域专家
    tools: []
    model_configs:
      - model_name: ollama/llama3:instruct
        provider: ollama
        max_tokens: 1024
        temperature: 0.7
        top_p: 0.9
        frequency_penalty: 0.0
        presence_penalty: 0.0
        is_primary: true
    """
)

FAKE_RESPONSE = "这是EnhancedWikiManager协作路径的确定性响应内容。"


async def fake_provider_generate(
    prompt, model=None, temperature=None, max_tokens=None, **kwargs
):
    """EnhancedWikiManager 边界模拟：真实 LiteLLMProvider 实例的方法替换。

    无 self 参数的普通 async 函数，赋给实例属性后
    `instance.generate(prompt, model=...)` 直接命中，无需联网。
    """
    return FAKE_RESPONSE, {"usage": {"total_tokens": len(FAKE_RESPONSE)}}


@pytest.fixture
def roles_dir(tmp_path):
    """真实 RoleModelManager 使用的角色 YAML 目录"""
    dir_path = tmp_path / "roles"
    dir_path.mkdir()
    (dir_path / "domain_expert.yaml").write_text(ROLE_YAML, encoding="utf-8")
    (dir_path / "researcher.yaml").write_text(
        ROLE_YAML
        .replace("llama3:instruct", "mistral:latest")
        .replace("领域专家", "研究员"),
        encoding="utf-8",
    )
    (dir_path / "editor.yaml").write_text(
        ROLE_YAML
        .replace("llama3:instruct", "gemma:latest")
        .replace("领域专家", "编辑"),
        encoding="utf-8",
    )
    return dir_path


@pytest.fixture
def real_role_model_manager(roles_dir):
    """真实 RoleModelManager，从临时 YAML 加载 3 个角色"""
    return RoleModelManager(roles_dir_path=str(roles_dir))


class TestRoleModelMappingContract:
    """RED 重定 #1：不同角色映射到不同模型 + debate 映射 1:1 契约"""

    def test_different_roles_map_to_different_models(self, real_role_model_manager):
        roles = ["domain_expert", "researcher", "editor"]
        mappings = [
            real_role_model_manager.get_role_model_mapping(role) for role in roles
        ]
        assert all(mapping is not None for mapping in mappings)
        models = {mapping.role_model_config.model_name for mapping in mappings}
        assert len(models) == 3
        assert models == {
            "ollama/llama3:instruct",
            "ollama/mistral:latest",
            "ollama/gemma:latest",
        }

    def test_get_debate_model_mappings_keeps_1to1_with_none_for_unknown(
        self, real_role_model_manager
    ):
        roles = ["domain_expert", "ghost_role", "editor"]
        mappings = real_role_model_manager.get_debate_model_mappings(roles)
        # 1:1 对应请求角色（含 None 占位，EnhancedDebateManager 校验会拒绝不完整映射）
        assert len(mappings) == len(roles)
        assert mappings[0] is not None
        assert mappings[0].role_name == "domain_expert"
        assert mappings[0].role_model_config.model_name == "ollama/llama3:instruct"
        assert mappings[1] is None
        assert mappings[2] is not None
        assert mappings[2].role_model_config.model_name == "ollama/gemma:latest"


class TestEnhancedWikiManagerCollaboration:
    """RED 重定 #2/#3：EnhancedWikiManager 真实依赖组装 + 协作方法与合成质量"""

    def make_enhanced_wiki(self, tmp_path, real_role_model_manager):
        provider = LiteLLMProvider(config=ProviderConfig(model="test-model"))
        provider.generate = fake_provider_generate
        return EnhancedWikiManager(
            wiki_root=tmp_path / "wiki",
            role_model_manager=real_role_model_manager,
            model_provider=provider,
        )

    def test_enhanced_wiki_manager_collaboration_method(
        self, tmp_path, real_role_model_manager
    ):
        enhanced = self.make_enhanced_wiki(tmp_path, real_role_model_manager)
        # 真实依赖齐备 -> 组装简化协作引擎；未提供 session/role manager -> 无原协作器
        assert enhanced.simple_collaboration_engine is not None
        assert enhanced.collaborator is None

        wiki_page = asyncio.run(
            enhanced.create_collaborative_wiki(
                title="机器学习测试",
                topic="机器学习算法原理与应用",
                roles=["domain_expert", "researcher"],
                rounds=1,
                show_progress=False,
            )
        )

        assert wiki_page is not None
        assert wiki_page.title == "机器学习测试"
        assert len(wiki_page.content) > 0
        assert wiki_page.file_path.exists()

        file_content = wiki_page.file_path.read_text(encoding="utf-8")
        assert "协作" in file_content or "collaboration" in file_content.lower()

    def test_content_synthesis_quality(self, tmp_path, real_role_model_manager):
        enhanced = self.make_enhanced_wiki(tmp_path, real_role_model_manager)
        wiki_page = asyncio.run(
            enhanced.create_collaborative_wiki(
                title="区块链技术",
                topic="区块链技术的原理和应用",
                roles=["domain_expert", "researcher", "editor"],
                rounds=1,
                show_progress=False,
            )
        )
        content = wiki_page.content

        content_structure_checks = [
            ("标题", "# 区块链技术" in content),
            ("章节划分", "## " in content),
            ("角色贡献", content.count(FAKE_RESPONSE) >= 3),
            ("结构化内容", len(content.strip()) > 100),
            ("协作标识", "协作" in content or "collaboration" in content.lower()),
        ]
        for check_name, check_result in content_structure_checks:
            assert check_result, f"内容质量检查失败: {check_name}"

        sections = content.split("##")
        assert len(sections) >= 3, (
            f"内容应该包含至少3个章节，但只有{len(sections)}个"
        )


class TestCollaborationProgressContract:
    """CollaborationProgress 时间戳契约（generated_content/errors/to_dict）"""

    def test_generated_content_entries_have_role_content_timestamp(self):
        progress = CollaborationProgress(total_steps=2)
        progress.update("domain_expert", "贡献内容", content="内容A")
        progress.update("researcher", "贡献内容", content="内容B")

        assert progress.current_step == 2
        assert len(progress.generated_content) == 2
        for entry in progress.generated_content:
            assert set(entry.keys()) == {"role", "content", "timestamp"}
            datetime.fromisoformat(entry["timestamp"])

    def test_error_entries_have_error_and_timestamp(self):
        progress = CollaborationProgress(total_steps=1)
        progress.add_error("模型调用失败")

        assert len(progress.errors) == 1
        assert progress.errors[0]["error"] == "模型调用失败"
        datetime.fromisoformat(progress.errors[0]["timestamp"])

    def test_to_dict_includes_start_time_elapsed_and_percentage(self):
        progress = CollaborationProgress(total_steps=4)
        progress.update("editor", "贡献内容", content="内容")

        data = progress.to_dict()
        assert data["total_steps"] == 4
        assert data["current_step"] == 1
        assert data["progress_percentage"] == pytest.approx(25.0)
        datetime.fromisoformat(data["start_time"])
        assert data["elapsed_seconds"] >= 0
        assert data["is_complete"] is False


class TestWikiManagerExceptionPaths:
    """WikiManager 真实异常路径（实测生产行为）"""

    def test_rejects_non_path_root(self):
        with pytest.raises(TypeError, match="wiki_root must be a Path object"):
            WikiManager(wiki_root="not_a_path")

    def test_create_page_duplicate_nonempty_raises(self, tmp_path):
        wiki = WikiManager(wiki_root=tmp_path / "wiki")
        content = (
            "机器学习是人工智能的核心分支，研究如何让计算机从数据中学习规律。"
            + "内容内容内容" * 20
        )
        wiki.create_page("机器学习", content)

        with pytest.raises(ValueError, match="already exists and contains content"):
            wiki.create_page("机器学习", "另一份非空内容。" + "填充" * 40)

    def test_create_page_empty_title_raises(self, tmp_path):
        wiki = WikiManager(wiki_root=tmp_path / "wiki")
        with pytest.raises(ValueError, match="Title cannot be empty"):
            wiki.create_page("", "")

    def test_update_page_not_found_raises(self, tmp_path):
        wiki = WikiManager(wiki_root=tmp_path / "wiki")
        with pytest.raises(ValueError, match="not found"):
            wiki.update_page("不存在的页面", "新内容")


class TestIntegrationGuards:
    """集成守卫：辩论管理器可达、依赖注入缺口显式报错、角色智能选择可用"""

    def test_debate_manager_integration_exists(self):
        from daip_live.p8_debate_system.enhanced_debate_manager import (
            EnhancedDebateManager,
        )
        assert EnhancedDebateManager is not None

    def test_dependency_injection_completeness(self, tmp_path):
        incomplete_wiki = EnhancedWikiManager(wiki_root=tmp_path / "wiki")
        assert incomplete_wiki.collaborator is None
        assert incomplete_wiki.simple_collaboration_engine is None

        with pytest.raises(RuntimeError, match="Cannot create collaborative wiki"):
            asyncio.run(
                incomplete_wiki.create_collaborative_wiki(
                    title="测试页面", topic="测试主题"
                )
            )

    def test_role_intelligence_selector_integration(self):
        from daip_live.wiki.role_intelligence_selector import (
            RoleIntelligenceSelector,
        )
        mock_role_manager = Mock()
        mock_role_manager.list_roles.return_value = [
            Mock(name="domain_expert"),
            Mock(name="researcher"),
            Mock(name="editor"),
        ]
        selector = RoleIntelligenceSelector(role_manager=mock_role_manager)
        roles = selector.analyze_topic_for_roles(
            "量子计算在密码学中的应用", max_roles=4
        )
        assert isinstance(roles, list)
        assert len(roles) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
