from src.personal_assistant.llm_manager import IntegratedLLMManager

class CasualChat:
    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager or IntegratedLLMManager()
        self.persona = "你现在是一位资深的软件工程师和创业导师，你的言行举止和思维方式都模仿Paul Graham。"

    def handle(self, history: list[str], user_input: str) -> str:
        prompt_history = "\n".join(history)
        prompt = f"{self.persona}\n\n{prompt_history}\n用户: {user_input}\nAI:"
        
        return self.llm_manager.get_response(prompt)

