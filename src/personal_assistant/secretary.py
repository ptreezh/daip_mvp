from src.personal_assistant.llm_manager import IntegratedLLMManager

class Secretary:
    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager or IntegratedLLMManager()
        self.persona = "你是一个专业的秘书，你需要根据用户的对话历史和当前输入，提炼出一个清晰、可执行的任务描述。"

    def refine(self, history: list[str], user_input: str) -> str:
        prompt_history = "\n".join(history)
        prompt = f"{self.persona}\n\n对话历史:\n{prompt_history}\n\n当前用户输入: {user_input}\n\n请提炼任务:"
        return self.llm_manager.get_response(prompt)
