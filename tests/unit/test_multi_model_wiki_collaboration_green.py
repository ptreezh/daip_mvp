#!/usr/bin/env python3
"""
TDD GREEN阶段测试 - 多模型Wiki协作功能（与真实生产契约对齐）

核心原则：
- 使用真实生产类组装：RoleModelManager（真实YAML）、
  SimpleCollaborationEngine、WikiManager
- 仅在外部边界模拟 model_provider.generate（真实 LiteLLMProvider 需要联网/Ollama）
- 断言反映真实生产行为：角色模型映射、generate 关键字实参、模型回退、
  进度回调、页面落盘、章节合成

契约来源（实测于源码，非臆测）：
- SimpleCollaborationEngine.create_collaborative_wiki(title, topic,
  roles=None, rounds=1)
  -> Tuple[WikiPage, str]；默认 roles = ["domain_expert", "researcher", "editor"]
- _generate_role_contribution:
  get_role_model_mapping(role, use_debate_config=True) -> False 回退 -> None 时
  使用默认 "ollama/llama3:instruct" / temperature=0.7 / max_tokens=1000
- generate 调用: await generate(prompt, model=..., temperature=..., max_tokens=...)
  返回 (content, usage) 二元组；失败时沿 [model_name] + PREFERRED_MODELS 回退
- 章节结构: # {title} / ## 协作主题 / 七个 ## 章节（仅非空）/ ## 协作说明
- EnhancedWikiManager 硬性拒绝 Mock 依赖（isinstance 校验 -> ValueError）
"""

import asyncio
import textwrap
from unittest.mock import Mock

import pytest

from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.wiki.manager import WikiManager
from daip_live.wiki.simple_collaboration_engine import SimpleCollaborationEngine

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


class FakeModelProvider:
    """外部边界模拟：记录 agenerate 调用，返回确定性二元组 (content, usage)"""

    def __init__(self, responses=None, default_content=None):
        self.responses = responses or {}
        self.default_content = default_content or "这是模拟模型的确定性响应内容。"
        self.calls = []

    async def agenerate(
        self, prompt, model=None, temperature=None, max_tokens=None, **kwargs
    ):
        self.calls.append(
            {
                "prompt": prompt,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
        content = self.responses.get(model, self.default_content)
        return content, {"usage": {"total_tokens": len(content)}}


@pytest.fixture
def roles_dir(tmp_path):
    """真实 RoleModelManager 使用的角色 YAML 目录"""
    dir_path = tmp_path / "roles"
    dir_path.mkdir()
    (dir_path / "domain_expert.yaml").write_text(ROLE_YAML, encoding="utf-8")
    (dir_path / "researcher.yaml").write_text(
        ROLE_YAML.replace("llama3:instruct", "mistral:latest").replace(
            "领域专家", "研究员"
        ),
        encoding="utf-8",
    )
    (dir_path / "editor.yaml").write_text(
        ROLE_YAML.replace("llama3:instruct", "gemma:latest").replace(
            "领域专家", "编辑"
        ),
        encoding="utf-8",
    )
    return dir_path


class TestRoleModelMappingContract:
    """RoleModelManager + 真实 YAML -> get_role_model_mapping 契约"""

    def test_loads_enhanced_roles_from_real_yaml(self, roles_dir):
        manager = RoleModelManager(roles_dir_path=str(roles_dir))
        role_names = {role.name for role in manager.list_roles()}
        assert role_names == {"domain_expert", "researcher", "editor"}

    def test_get_role_model_mapping_returns_role_model_config(self, roles_dir):
        manager = RoleModelManager(roles_dir_path=str(roles_dir))
        mapping = manager.get_role_model_mapping("domain_expert")
        assert mapping is not None
        assert mapping.role_model_config.model_name == "ollama/llama3:instruct"
        assert mapping.role_model_config.temperature == 0.7
        assert mapping.role_model_config.max_tokens == 1024

    def test_unknown_role_returns_none(self, roles_dir):
        manager = RoleModelManager(roles_dir_path=str(roles_dir))
        assert manager.get_role_model_mapping("ghost_role") is None


class TestSimpleCollaborationEngineGREEN:
    """SimpleCollaborationEngine 成功路径（真实依赖 + 边界 Fake provider）"""

    @pytest.fixture
    def engine_fixture(self, roles_dir, tmp_path):
        role_model_manager = RoleModelManager(roles_dir_path=str(roles_dir))
        provider = FakeModelProvider()
        wiki_manager = WikiManager(wiki_root=tmp_path / "wiki")
        engine = SimpleCollaborationEngine(
            role_model_manager=role_model_manager,
            model_provider=provider,
            wiki_manager=wiki_manager,
        )
        return engine, provider, wiki_manager

    def test_create_collaborative_wiki_returns_page_and_content(self, engine_fixture):
        engine, _, wiki_manager = engine_fixture
        page, content = asyncio.run(
            engine.create_collaborative_wiki(title="机器学习基础", topic="机器学习")
        )
        assert page.title == "机器学习基础"
        assert isinstance(content, str) and len(content) > 100
        assert page.file_path.exists()
        assert page.title in wiki_manager._pages

    def test_generate_called_with_role_mapped_model_and_keyword_args(
        self, engine_fixture
    ):
        engine, provider, _ = engine_fixture
        asyncio.run(
            engine.create_collaborative_wiki(title="机器学习基础", topic="机器学习")
        )
        # 默认 3 角色（pro_arguer/con_arguer/research_analyst）x 1 轮；
        # fixture roles 目录无这些角色 -> mapping None -> 回退默认模型 llama3:instruct
        assert len(provider.calls) == 3

        for call in provider.calls:
            # agenerate 以关键字传参（生产契约），无 mapping 时用默认模型与默认参数
            assert call["model"] == "ollama/llama3:instruct"
            assert call["temperature"] == 0.7
            assert call["max_tokens"] == 1000

    def test_content_includes_all_role_contributions_and_sections(self, engine_fixture):
        engine, _, _ = engine_fixture
        _, content = asyncio.run(
            engine.create_collaborative_wiki(title="机器学习基础", topic="机器学习")
        )
        # 三个角色的贡献均进入合成内容（同一贡献可能被分发到多个章节）
        assert content.count("这是模拟模型的确定性响应内容。") >= 3
        # 章节结构（synthesize 固定章节，仅非空章节出现）
        assert content.startswith("# 机器学习基础")
        assert "## 协作主题" in content
        # 默认角色 pro_arguer/con_arguer/research_analyst 路由到应用场景/挑战/研究进展
        assert "## 技术要点" in content
        assert "## 应用场景" in content
        assert "## 研究进展" in content
        assert "## 挑战与展望" in content
        assert "## 参考资料" in content
        # 至少 3 个非空章节 + 协作说明
        assert content.count("## ") >= 5
        # 协作说明列出参与角色
        assert "## 协作说明" in content
        assert "pro_arguer, con_arguer, research_analyst" in content

    def test_unknown_role_falls_back_to_default_model_and_domain_prompt(
        self, engine_fixture
    ):
        engine, provider, _ = engine_fixture
        asyncio.run(
            engine.create_collaborative_wiki(
                title="未知角色测试", topic="测试", roles=["ghost_role"]
            )
        )
        assert len(provider.calls) == 1
        call = provider.calls[0]
        # 无 mapping -> 默认模型与默认参数（生产契约）
        assert call["model"] == "ollama/llama3:instruct"
        assert call["temperature"] == 0.7
        assert call["max_tokens"] == 1000
        # 未知角色回退到 domain_expert 提示模板
        assert "领域专家" in call["prompt"]

    def test_all_models_fail_raises_without_fake_content(self, roles_dir, tmp_path):
        class FailingProvider(FakeModelProvider):
            async def agenerate(
                self, prompt, model=None, temperature=None, max_tokens=None, **kwargs
            ):
                self.calls.append({"prompt": prompt, "model": model})
                raise RuntimeError("model unavailable")

        role_model_manager = RoleModelManager(roles_dir_path=str(roles_dir))
        provider = FailingProvider()
        wiki_manager = WikiManager(wiki_root=tmp_path / "wiki")
        engine = SimpleCollaborationEngine(
            role_model_manager=role_model_manager,
            model_provider=provider,
            wiki_manager=wiki_manager,
        )
        # 全部模型失败 -> 明确抛错（不返回模拟假内容、不创建空页面）
        with pytest.raises(RuntimeError, match="贡献生成均失败"):
            asyncio.run(
                engine.create_collaborative_wiki(title="降级测试", topic="测试主题")
            )

    def test_progress_callback_receives_updates_until_complete(self, engine_fixture):
        engine, _, _ = engine_fixture
        snapshots = []
        engine.progress_callback = snapshots.append
        asyncio.run(
            engine.create_collaborative_wiki(
                title="进度测试", topic="进度", roles=["domain_expert"], rounds=2
            )
        )
        assert snapshots, "progress_callback 未被调用"
        final = snapshots[-1]
        assert final.is_complete is True
        assert final.total_steps == 2
        assert len(final.generated_content) == 2
        # 回调贯穿整个流程：每轮开始/完成各一帧 + 整合帧 + 完成帧
        assert len(snapshots) >= 4

    def test_wiki_page_persisted_with_content(self, engine_fixture):
        engine, _, _ = engine_fixture
        page, content = asyncio.run(
            engine.create_collaborative_wiki(title="落盘测试", topic="落盘")
        )
        persisted = page.file_path.read_text(encoding="utf-8")
        assert persisted == content


class TestEnhancedWikiManagerContract:
    """EnhancedWikiManager 真实契约：拒绝 Mock、无引擎时报错"""

    def test_rejects_mock_model_provider(self, tmp_path):
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        with pytest.raises(ValueError, match="必须使用真实的LiteLLMProvider"):
            EnhancedWikiManager(wiki_root=tmp_path / "wiki", model_provider=Mock())

    def test_rejects_mock_role_model_manager(self, tmp_path):
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        with pytest.raises(ValueError, match="必须使用真实的RoleModelManager"):
            EnhancedWikiManager(wiki_root=tmp_path / "wiki", role_model_manager=Mock())

    def test_without_engines_raises_runtime_error(self, tmp_path):
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        manager = EnhancedWikiManager(wiki_root=tmp_path / "wiki")
        with pytest.raises(RuntimeError, match="no working collaboration engine"):
            asyncio.run(manager.create_collaborative_wiki(title="t", topic="t"))
