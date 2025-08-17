import pytest
from unittest.mock import Mock, patch

# This import will fail initially, which is expected for the RED step.
from src.personal_assistant.casual_chat import CasualChat

@pytest.fixture
def mock_llm_manager():
    """Fixture to create a mock IntegratedLLMManager."""
    mock = Mock()
    mock.get_response.return_value = "这是一个模拟的LLM响应。"
    return mock

def test_casual_chat_prompt(mock_llm_manager):
    """
    Tests that the casual chat handler builds a prompt with the correct persona.
    Corresponds to T-PA-V3.1-05.
    """
    with patch('src.personal_assistant.casual_chat.IntegratedLLMManager', return_value=mock_llm_manager):
        chat = CasualChat()
        chat.handle("你好")
        
        mock_llm_manager.get_response.assert_called_once()
        prompt = mock_llm_manager.get_response.call_args[0][0]
        assert "你现在是一位资深的软件工程师和创业导师，你的言行举止和思维方式都模仿Paul Graham。" in prompt
        assert "你好" in prompt

def test_casual_chat_maintains_history(mock_llm_manager):
    """
    Tests that the casual chat handler maintains conversation history.
    Corresponds to T-PA-V3.1-07.
    """
    chat = CasualChat(llm_manager=mock_llm_manager)

    # First interaction
    first_response = "当然，我一直在思考关于价值创造的问题。"
    mock_llm_manager.get_response.return_value = first_response
    chat.handle("最近在忙什么？")

    # Second interaction
    second_response = "这是一个很好的问题。我认为关键在于专注和执行力。"
    mock_llm_manager.get_response.return_value = second_response
    chat.handle("如何才能成为一个优秀的创业者？")

    assert mock_llm_manager.get_response.call_count == 2
    
    # Check the prompt for the second call
    second_prompt = mock_llm_manager.get_response.call_args[0][0]
    assert "用户: 最近在忙什么？" in second_prompt
    assert f"AI: {first_response}" in second_prompt
    assert "用户: 如何才能成为一个优秀的创业者？" in second_prompt