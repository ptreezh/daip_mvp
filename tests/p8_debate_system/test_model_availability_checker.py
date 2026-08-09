"""
模型可用性检查器防回归测试

背景（2026-08-09 实测复现）：checker 曾对嵌入模型 nomic-embed-text 调用
generate()（chat 接口），Ollama 返回 "does not support generate"，异常被误分类
为"无法连接到模型服务"，导致 perform_model_check 失败、辩论无法启动。

修复目标：
- 嵌入模型（embedding_model）必须走 embed() 检查
- 对话模型（default_model）必须走 generate() 检查
- "does not support" 类错误必须分类为模型类型误用，而非连接错误
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from daip_live.p8_debate_system.model_availability_checker import (
    ModelAvailabilityChecker,
)


def _fake_generate(prompt, params=None):
    """构造 async generator 契约的 generate 替身。"""

    async def _gen():
        yield "hello from mock"

    return _gen()


@pytest.fixture
def fake_provider():
    provider = MagicMock()
    provider.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])
    provider.generate = MagicMock(side_effect=_fake_generate)
    return provider


@pytest.fixture
def checker():
    return ModelAvailabilityChecker(
        default_model="ollama/llama3:latest",
        embedding_model="ollama/nomic-embed-text",
    )


class TestModelAvailabilityChecker:
    @pytest.mark.asyncio
    async def test_embedding_model_checked_via_embed(self, fake_provider, checker):
        """嵌入模型必须走 embed() 检查，绝不走 generate()。"""
        with patch(
            "daip_live.p8_debate_system.model_availability_checker.LiteLLMProvider",
            return_value=fake_provider,
        ):
            ok, msg = await checker.check_model_availability(
                "ollama/nomic-embed-text", is_embedding=True
            )

        assert ok
        assert msg == ""
        fake_provider.embed.assert_awaited_once()
        fake_provider.generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_chat_model_checked_via_generate(self, fake_provider, checker):
        """对话模型必须走 generate() 检查。"""
        with patch(
            "daip_live.p8_debate_system.model_availability_checker.LiteLLMProvider",
            return_value=fake_provider,
        ):
            ok, msg = await checker.check_model_availability(
                "ollama/llama3:latest", is_embedding=False
            )

        assert ok
        assert msg == ""
        fake_provider.generate.assert_called_once()
        fake_provider.embed.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_all_models_routes_embedding(self, fake_provider, checker):
        """check_all_models 必须把嵌入模型路由到 embed()、对话模型路由到 generate()。"""
        with patch(
            "daip_live.p8_debate_system.model_availability_checker.LiteLLMProvider",
            return_value=fake_provider,
        ):
            all_ok, errors = await checker.check_all_models()

        assert all_ok
        assert errors == []
        fake_provider.embed.assert_awaited_once()
        fake_provider.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_does_not_support_error_classified_as_model_misuse(self, checker):
        """'does not support' 必须归类为模型类型误用，而非连接错误。"""
        provider = MagicMock()

        async def _raise_generator(prompt, params=None):
            raise RuntimeError(
                "OllamaException - "
                '{"error":"\\"nomic-embed-text\\" does not support generate"}'
            )
            yield  # pragma: no cover - unreachable

        provider.generate = MagicMock(side_effect=_raise_generator)
        with patch(
            "daip_live.p8_debate_system.model_availability_checker.LiteLLMProvider",
            return_value=provider,
        ):
            ok, msg = await checker.check_model_availability(
                "ollama/nomic-embed-text", is_embedding=False
            )

        assert not ok
        assert "不支持" in msg
        assert "无法连接" not in msg
