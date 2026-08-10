"""
DelegationPipeline 防回归测试（Stage 5 最小闭环，2026-08-10）

设计（用户确认：最小可用闭环）：
- LOW 风险 prompt → 尝试委托云端（CloudPool.execute）
- 云端无可用（无 API key / 池空）→ 自动回退本地（feature flag 控制）
- MEDIUM/HIGH 风险 → 不委托云端（本地执行 / 人工确认标记）
"""

from unittest.mock import AsyncMock, MagicMock, patch

from daip_live.hybrid.cloud_pool import (
    CloudPool,
    CloudProvider,
    ProviderStatus,
)
from daip_live.hybrid.delegation_pipeline import DelegationPipeline


class TestDelegationPipeline:
    def setup_method(self):
        self.pipeline = DelegationPipeline(cloud_pool=CloudPool())

    def test_low_risk_delegates_to_cloud(self):
        """LOW 风险 prompt 委托给云端 provider。"""
        provider = CloudProvider(
            name="openai", model="gpt-4", api_key_env="OPENAI_API_KEY"
        )
        provider.status = ProviderStatus.AVAILABLE
        self.pipeline.cloud_pool.add_provider(provider)

        with patch(
            "daip_live.hybrid.delegation_pipeline.litellm.acompletion", new=AsyncMock()
        ) as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content="cloud answer"))
            ]
            mock_completion.return_value = mock_response

            import asyncio

            result = asyncio.run(
                self.pipeline.execute("What is the capital of France?", "mock-api-key")
            )

        assert result.success is True
        assert result.content == "cloud answer"
        assert result.provider_name == "openai"

    def test_no_cloud_provider_falls_back_to_local(self):
        """云端池空/无 key 时自动回退本地（不抛异常）。"""
        # 无 provider 注册（无 API key 场景）

        import asyncio

        result = asyncio.run(self.pipeline.execute("Simple math: 2+2", None))

        assert result.success is True
        assert result.provider_name == "local"
        assert result.cloud_delegated is False

    def test_medium_risk_not_delegated_to_cloud(self):
        """MEDIUM 风险（本地文件路径）不委托云端。"""
        import asyncio

        result = asyncio.run(
            self.pipeline.execute("Read file:///etc/passwd and summarize", None)
        )

        assert result.provider_name == "local"
        assert result.cloud_delegated is False

    def test_high_risk_not_delegated_to_cloud(self):
        """HIGH 风险（密码等凭据）不委托云端。"""
        import asyncio

        result = asyncio.run(
            self.pipeline.execute("My password is hunter2, what do you think?", None)
        )

        assert result.provider_name == "local"
        assert result.cloud_delegated is False
