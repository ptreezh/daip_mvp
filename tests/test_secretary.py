import pytest
from unittest.mock import Mock, patch

# This import will fail initially, which is expected for the RED step.
from src.personal_assistant.secretary import Secretary

@pytest.fixture
def mock_llm_manager():
    """Fixture to create a mock IntegratedLLMManager."""
    mock = Mock()
    mock.get_response.return_value = "这是一个模拟的LLM响应，代表了提炼后的任务。"
    return mock

def test_secretary_refines_task(mock_llm_manager):
    """
    Tests that the secretary correctly builds a prompt to refine a task.
    Corresponds to T-PA-V3.1-09.
    """
    secretary = Secretary(llm_manager=mock_llm_manager)
    user_history = ["用户: 帮我规划一下明天的日程。", "AI: 好的，请问明天有什么特别的安排吗？"]
    user_input = "我需要参加一个重要的会议，然后和朋友吃饭。"
    
    secretary.refine(user_history, user_input)
    
    mock_llm_manager.get_response.assert_called_once()
    prompt = mock_llm_manager.get_response.call_args[0][0]
    
    assert "你是一个专业的秘书" in prompt
    assert "用户: 帮我规划一下明天的日程。" in prompt
    assert "AI: 好的，请问明天有什么特别的安排吗？" in prompt
    assert "我需要参加一个重要的会议，然后和朋友吃饭。" in prompt
