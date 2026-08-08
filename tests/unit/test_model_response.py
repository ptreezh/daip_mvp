"""模型响应单元测试 - 对齐 LiteLLMProvider / EnhancedDebateManager 真实 API"""

from unittest.mock import AsyncMock, Mock, patch

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
    """generate 是 async 且返回 (content, usage) 二元组"""
    provider = LiteLLMProvider(config=Mock())
    with patch.object(
        LiteLLMProvider, "generate", new=AsyncMock(return_value=("ok", {"total_tokens": 5}))
    ) as mock_generate:
        content, usage = await provider.generate("prompt", params={"model": "gpt-4"})

    assert content == "ok"
    assert usage == {"total_tokens": 5}
    mock_generate.assert_awaited_once_with("prompt", params={"model": "gpt-4"})


@pytest.mark.asyncio
async def test_generate_response_with_model_uses_role_provider():
    """legacy 方法通过角色模型配置的 provider 生成回复"""
    manager = _build_manager()
    mock_provider = Mock()
    mock_provider.generate = AsyncMock(return_value=("Test response", {"total_tokens": 10}))
    with patch.object(manager, "_get_model_provider_for_config", return_value=mock_provider) as mock_get:
        response_content, token_info = await manager._generate_response_with_model(
            topic="Should AI be regulated?",
            role=Mock(persona="你是一个乐观主义者"),
            role_mapping=Mock(model_config=Mock(
                model_name="gpt-4", temperature=0.7, max_tokens=512,
                top_p=0.9, frequency_penalty=0.0, presence_penalty=0.0,
            )),
            history=[],
        )

    assert response_content == "Test response"
    assert token_info == {"total_tokens": 10}
    mock_get.assert_called_once()
    mock_provider.generate.assert_awaited_once()
    call_kwargs = mock_provider.generate.await_args.kwargs
    assert call_kwargs["model"] == "gpt-4"
    assert call_kwargs["temperature"] == 0.7
    assert "Should AI be regulated?" in mock_provider.generate.await_args.args[0]


@pytest.mark.asyncio
async def test_generate_response_with_model_propagates_model_error():
    """模型错误沿调用链向上传播"""
    manager = _build_manager()
    mock_provider = Mock()
    mock_provider.generate = AsyncMock(side_effect=ModelError("model error"))
    with patch.object(manager, "_get_model_provider_for_config", return_value=mock_provider):
        with pytest.raises(ModelError, match="model error"):
            await manager._generate_response_with_model(
                topic="t",
                role=Mock(persona="p"),
                role_mapping=Mock(model_config=Mock(
                    model_name="gpt-4", temperature=0.7, max_tokens=512,
                    top_p=0.9, frequency_penalty=0.0, presence_penalty=0.0,
                )),
                history=[],
            )
