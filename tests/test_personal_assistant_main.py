import pytest
from unittest.mock import Mock, patch

# This import will fail initially, which is expected for the RED step.
from interactive_cli import start_personal_assistant

@pytest.fixture
def mock_intent_classifier():
    mock = Mock()
    mock.classify.return_value = "闲聊"
    return mock

@pytest.fixture
def mock_casual_chat():
    mock = Mock()
    return mock

def test_main_loop_dispatches_to_casual_chat(
    mock_intent_classifier, mock_casual_chat
):
    """
    Tests that the main loop dispatches to the casual chat handler.
    Corresponds to T-PA-V3.1-15.
    """
    with patch('interactive_cli.IntentClassifier', return_value=mock_intent_classifier), \
         patch('interactive_cli.CasualChat', return_value=mock_casual_chat), \
         patch('builtins.input', side_effect=['你好', 'exit']):

        start_personal_assistant()

        mock_intent_classifier.classify.assert_called_with("你好")
        mock_casual_chat.handle.assert_called_once_with("你好")

@pytest.fixture
def mock_complex_task_handler():
    mock = Mock()
    return mock

def test_main_loop_dispatches_to_complex_task(
    mock_intent_classifier, mock_complex_task_handler
):
    """
    Tests that the main loop dispatches to the complex task handler.
    Corresponds to T-PA-V3.1-17.
    """
    mock_intent_classifier.classify.return_value = "复杂任务"
    
    with patch('interactive_cli.IntentClassifier', return_value=mock_intent_classifier), \
         patch('interactive_cli.ComplexTaskHandler', return_value=mock_complex_task_handler), \
         patch('builtins.input', side_effect=['帮我查天气', 'exit']):

        start_personal_assistant()

        mock_intent_classifier.classify.assert_called_with("帮我查天气")
        mock_complex_task_handler.handle.assert_called_once_with([], "帮我查天气")