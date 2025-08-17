from src.personal_assistant.llm_manager import IntegratedLLMManager

class Planner:
    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager or IntegratedLLMManager()
        self.persona = "你是一个专业的任务规划师，你需要根据用户提炼后的任务和可用的API，生成一个JSON格式的、可执行的计划。"

    def plan(self, refined_task: str, api_list: list[str]) -> str:
        api_list_str = "\n".join([f"- `{api}`" for api in api_list])
        prompt = f"""{self.persona}

任务: {refined_task}

可用的API:
{api_list_str}

请生成JSON格式的计划:
"""
        return self.llm_manager.get_response(prompt)
