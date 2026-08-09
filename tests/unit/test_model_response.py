"""模型响应单元测试 - 对齐 LiteLLMProvider / EnhancedDebateManager 真实 API"""

from unittest.mock import Mock, patch

import pytest

from daip_live.core.exceptions import ModelError
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager


def _build_manager() -> EnhancedDebateManager:
    return EnhancedDebateManager(
        session_manager=Mock(),
        role_manager=Mock(),
        role_model_manager=Mock(),
        model_provider=Mock(),
        use_optimized_architecture=False,
    )


@pytest.mark.asyncio
async def test_litellm_provider_generate_contract():
    """generate 是 async generator，调用方用 async for 收集内容"""
    provider = LiteLLMProvider(config=Mock())

    async def _fake_generate(self, prompt, params=None, **kwargs):
        yield "ok"

    with patch.object(LiteLLMProvider, "generate", new=_fake_generate):
        content = None
        async for chunk in provider.generate("prompt", params={"model": "gpt-4"}):
            content = chunk

    assert content == "ok"


@pytest.mark.asyncio
async def test_generate_response_with_model_uses_role_provider():
    """legacy 方法通过角色模型配置的 provider 生成回复"""
    manager = _build_manager()
    mock_provider = Mock()

    async def _fake_generate(prompt, params=None):
        yield "Test response"

    mock_provider.generate = _fake_generate
    with patch.object(
        manager, "_get_model_provider_for_config", return_value=mock_provider
    ) as mock_get:
        response_content, token_info = await manager._generate_response_with_model(
            topic="Should AI be regulated?",
            role=Mock(persona="你是一个乐观主义者"),
            role_mapping=Mock(
                model_config=Mock(
                    model_name="gpt-4",
                    temperature=0.7,
                    max_tokens=512,
                    top_p=0.9,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                )
            ),
            history=[],
        )

    assert response_content == "Test response"
    mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_generate_response_with_model_propagates_model_error():
    """模型错误沿调用链向上传播"""
    manager = _build_manager()
    mock_provider = Mock()

    async def _fake_generate_error(prompt, params=None):
        raise ModelError("model error")
        yield  # pragma: no cover

    mock_provider.generate = _fake_generate_error
    with patch.object(
        manager, "_get_model_provider_for_config", return_value=mock_provider
    ):
        with pytest.raises(ModelError, match="model error"):
            await manager._generate_response_with_model(
                topic="t",
                role=Mock(persona="p"),
                role_mapping=Mock(
                    model_config=Mock(
                        model_name="gpt-4",
                        temperature=0.7,
                        max_tokens=512,
                        top_p=0.9,
                        frequency_penalty=0.0,
                        presence_penalty=0.0,
                    )
                ),
                history=[],
            )
