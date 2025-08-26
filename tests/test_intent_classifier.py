# import pytest
# from unittest.mock import Mock, patch

# # This import will fail initially, which is expected for the RED step.
# from src.personal_assistant.intent_classifier import IntentClassifier

# @pytest.fixture
# def mock_llm_manager():
#     """Fixture to create a mock IntegratedLLMManager."""
#     mock = Mock()
#     # Simulate the LLM returning "闲聊" when the prompt contains "分类器"
#     mock.get_response.side_effect = lambda prompt, **kwargs: "闲聊" if "分类器" in prompt else "未知"
#     return mock

# def test_classify_as_casual_chat(mock_llm_manager):
#     """
#     Tests that the classifier correctly identifies a casual chat intent.
#     Corresponds to T-PA-V3.1-01.
#     """
#     # Patch the IntegratedLLMManager to use our mock
#     with patch('src.personal_assistant.intent_classifier.IntegratedLLMManager', return_value=mock_llm_manager):
#         classifier = IntentClassifier()
#         intent = classifier.classify("你好，今天天气怎么样？")
#         assert intent == "闲聊"
#         # Verify that the get_response method was called with a prompt containing "分类器"
#         mock_llm_manager.get_response.assert_called_once()
#         assert "分类器" in mock_llm_manager.get_response.call_args[0][0]

# def test_classify_as_complex_task(mock_llm_manager):
#     """
#     Tests that the classifier correctly identifies a complex task intent.
#     Corresponds to T-PA-V3.1-03.
#     """
#     # Modify the mock to return "复杂任务" for this test
#     mock_llm_manager.get_response.side_effect = lambda prompt, **kwargs: "复杂任务" if "分类器" in prompt else "未知"

#     with patch('src.personal_assistant.intent_classifier.IntegratedLLMManager', return_value=mock_llm_manager):
#         classifier = IntentClassifier()
#         intent = classifier.classify("帮我查询一下今天北京的天气，并制定一个半天的出行计划。")
#         assert intent == "复杂任务"
#         mock_llm_manager.get_response.assert_called_once()
#         assert "分类器" in mock_llm_manager.get_response.call_args[0][0]