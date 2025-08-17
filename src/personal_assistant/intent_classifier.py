from src.personal_assistant.llm_manager import IntegratedLLMManager

class IntentClassifier:
    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager or IntegratedLLMManager()

    def classify(self, text: str) -> str:
        prompt = f"""
        这是一个意图分类器。根据用户的输入，判断意图是“闲聊”还是“复杂任务”。
        用户输入: "{text}"
        意图是:
        """
        response = self.llm_manager.get_response(prompt)
        return response.strip()
