# import pytest
# from unittest.mock import Mock, patch

# # This import will fail initially, which is expected for the RED step.
# from src.personal_assistant.planner import Planner

# @pytest.fixture
# def mock_llm_manager():
#     """Fixture to create a mock IntegratedLLMManager."""
#     mock = Mock()
#     mock.get_response.return_value = "这是一个模拟的LLM响应，代表了生成的计划。"
#     return mock

# def test_planner_creates_plan(mock_llm_manager):
#     """
#     Tests that the planner correctly builds a prompt to generate a plan.
#     Corresponds to T-PA-V3.1-11.
#     """
#     planner = Planner(llm_manager=mock_llm_manager)
#     refined_task = "查询今天北京的天气，并制定一个半天的出行计划。"
#     api_list = ["search_weather(city: str)", "create_travel_plan(duration: str, activities: list[str])"]
#     
#     planner.plan(refined_task, api_list)
#     
#     mock_llm_manager.get_response.assert_called_once()
#     prompt = mock_llm_manager.get_response.call_args[0][0]
#     
#     assert "你是一个专业的任务规划师" in prompt
#     assert "可用的API" in prompt
#     assert "search_weather(city: str)" in prompt
#     assert "create_travel_plan(duration: str, activities: list[str])" in prompt
#     assert refined_task in prompt