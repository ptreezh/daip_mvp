"""
DelegationPipeline 防回归测试（Stage 5 最小闭环 v3，2026-08-10）

核心设计原则（用户明确）：
1. 全局上下文（系统提示/会话历史/长时记忆）永不上传云端
2. 所有任务先用**本地模型**分解为 >=3 个子任务
3. 子任务上下文完备自包含，不携带父任务/全局上下文
4. 子任务在子任务层面分发（可分发不同云端模型）
5. 云端不可用 / 分解失败 / 高风险 → 回退本地

测试策略：mock 本地分解（返回固定子任务），只验证与云端交互的约束。
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from daip_live.hybrid.cloud_pool import CloudPool, CloudProvider, ProviderStatus
from daip_live.hybrid.delegation_pipeline import DelegationPipeline


def _make_pipeline_with_provider(
    name="openai", model="gpt-4", status=ProviderStatus.AVAILABLE
):
    """构造含一个可用云端 provider 的 pipeline。"""
    provider = CloudProvider(name=name, model=model, api_key_env="TEST_API_KEY")
    provider.status = status
    pool = CloudPool()
    pool.add_provider(provider)
    return DelegationPipeline(cloud_pool=pool), provider


def _stub_decomposer(pipeline, subtasks):
    """mock 本地分解，返回固定子任务（隔离真实 Ollama）。"""
    return patch.object(
        pipeline,
        "_decompose_with_local_model",
        new=AsyncMock(return_value=subtasks),
    )


class TestDelegationPipelineV3:
    def test_global_context_never_sent_to_cloud_or_subtasks(self):
        """全局上下文绝不进云端消息，也不进入子任务。"""
        pipeline, provider = _make_pipeline_with_provider()
        global_context = (
            "User is a climate researcher from Shanghai, prefers Chinese, "
            "session history: discussed carbon markets earlier"
        )
        subtasks = [
            "Summarize the impact of climate change on agriculture",
            "List adaptation strategies for coastal cities",
            "Describe policy recommendations for emission reduction",
        ]

        sent_messages = []

        async def fake_cloud(**kwargs):
            sent_messages.append(kwargs.get("messages", []))
            response = MagicMock()
            response.choices = [
                MagicMock(message=MagicMock(content="subtask answer"))
            ]
            response.usage = MagicMock(total_tokens=10)
            return response

        with _stub_decomposer(pipeline, subtasks), patch(
            "daip_live.hybrid.delegation_pipeline.litellm.acompletion",
            new=AsyncMock(side_effect=fake_cloud),
        ):
            result = asyncio.run(
                pipeline.execute(
                    "Write a detailed report about climate change impacts",
                    api_key="test-key",
                    global_context=global_context,
                )
            )

        # 云端只收子任务文本，绝不含全局上下文
        assert result.cloud_delegated is True
        assert len(sent_messages) >= 3
        for messages in sent_messages:
            joined = str(messages).lower()
            assert "shanghai" not in joined
            assert "session history" not in joined
            assert "prefers chinese" not in joined

        # 子任务本身不含全局上下文
        for st in result.subtasks:
            assert "shanghai" not in st.task.lower()

    def test_task_decomposed_into_at_least_3_subtasks(self):
        """任务分解为 >=3 个子任务后才分发。"""
        pipeline, provider = _make_pipeline_with_provider()

        async def fake_cloud(**kwargs):
            response = MagicMock()
            response.choices = [
                MagicMock(message=MagicMock(content="subtask answer"))
            ]
            response.usage = MagicMock(total_tokens=10)
            return response

        with _stub_decomposer(
            pipeline,
            [
                "Analyze AI impact on healthcare",
                "Analyze AI impact on education",
                "Analyze AI impact on manufacturing",
            ],
        ), patch(
            "daip_live.hybrid.delegation_pipeline.litellm.acompletion",
            new=AsyncMock(side_effect=fake_cloud),
        ):
            result = asyncio.run(
                pipeline.execute(
                    "Analyze AI economic impact", api_key="test-key"
                )
            )

        assert result.cloud_delegated is True
        assert result.subtask_count >= 3

    def test_decompose_prompt_requires_self_contained_subtasks(self):
        """分解 prompt 必须要求子任务自包含、禁止全局上下文。"""
        pipeline, provider = _make_pipeline_with_provider()

        # 记录传给本地分解模型的 prompt
        decompose_prompts = []

        async def fake_decompose(task):
            decompose_prompts.append(task)
            return [
                "Subtask one generic",
                "Subtask two generic",
                "Subtask three generic",
            ]

        with patch.object(
            pipeline,
            "_decompose_with_local_model",
            new=AsyncMock(side_effect=fake_decompose),
        ), patch(
            "daip_live.hybrid.delegation_pipeline.litellm.acompletion",
            new=AsyncMock(),
        ) as mock_cloud:
            async def fake_cloud(**kwargs):
                response = MagicMock()
                response.choices = [
                    MagicMock(message=MagicMock(content="a"))
                ]
                response.usage = MagicMock(total_tokens=1)
                return response

            mock_cloud.side_effect = fake_cloud

            asyncio.run(
                pipeline.execute(
                    "Do a comprehensive economic analysis",
                    api_key="test-key",
                    global_context="HIGHLY SECRET internal data DONT LEAK",
                )
            )

    def test_subtasks_distribute_to_different_providers(self):
        """子任务分发到不同云端模型（多 provider 轮询）。"""
        provider1 = CloudProvider(
            name="openai", model="gpt-4", api_key_env="TEST_API_KEY"
        )
        provider1.status = ProviderStatus.AVAILABLE
        provider2 = CloudProvider(
            name="anthropic", model="claude-3", api_key_env="TEST_API_KEY"
        )
        provider2.status = ProviderStatus.AVAILABLE
        pool = CloudPool()
        pool.add_provider(provider1)
        pool.add_provider(provider2)
        pipeline = DelegationPipeline(cloud_pool=pool)

        used_providers = set()

        async def fake_cloud(**kwargs):
            used_providers.add(kwargs.get("model", "unknown"))
            response = MagicMock()
            response.choices = [
                MagicMock(message=MagicMock(content="subtask answer"))
            ]
            response.usage = MagicMock(total_tokens=10)
            return response

        with _stub_decomposer(
            pipeline,
            [
                "Compare US fiscal policy",
                "Compare China fiscal policy",
                "Compare EU fiscal policy",
            ],
        ), patch(
            "daip_live.hybrid.delegation_pipeline.litellm.acompletion",
            new=AsyncMock(side_effect=fake_cloud),
        ):
            result = asyncio.run(
                pipeline.execute(
                    "Compare economic policies", api_key="test-key"
                )
            )

        assert result.cloud_delegated is True
        assert len(used_providers) >= 2

    def test_no_cloud_available_falls_back_to_local(self):
        """无可用云端时回退本地。"""
        pipeline = DelegationPipeline(cloud_pool=CloudPool())

        with _stub_decomposer(
            pipeline,
            ["Subtask one", "Subtask two", "Subtask three"],
        ):
            result = asyncio.run(
                pipeline.execute("Summarize key points", api_key=None)
            )

        assert result.success is True
        assert result.cloud_delegated is False
        assert result.provider_name == "local"
        assert result.subtask_count >= 3

    def test_high_risk_never_delegated(self):
        """HIGH 风险（凭据）即使有云端也不委托。"""
        pipeline, provider = _make_pipeline_with_provider()

        result = asyncio.run(
            pipeline.execute(
                "My api key is sk-abcdef123456 and password is hunter2",
                api_key="test-key",
            )
        )

        assert result.cloud_delegated is False
        assert result.needs_human_approval is True
