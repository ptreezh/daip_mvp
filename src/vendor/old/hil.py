from src.orchestrator import Orchestrator


class HumanInteractionLayer:
    def __init__(self, orchestrator_instance: Orchestrator):  # 接收 Orchestrator 实例并指定类型
        self.orchestrator = orchestrator_instance  # 存储实例

    async def run_cli(self, input_provider=None):  # <--- 支持传入 input_provider
        print("欢迎来到 DAIP-L.I.V.E. P0 MVP 命令行界面。输入 'exit' 退出。")
        if input_provider is None:
            input_provider = input
        while True:
            print("[CLI] 等待用户输入 ...")
            user_input = input_provider("您: ")
            print(f"[CLI] 收到输入: {user_input}")
            if user_input.lower() == "exit":
                print("感谢使用 DAIP-L.I.V.E.，再见！")
                break
            try:
                print("[CLI] 调用 orchestrator 处理命令 ...")
                response = await self.orchestrator.process_command(
                    user_input,
                )  # <--- await 调用
                print(f"[CLI] orchestrator 响应: {response}")
            except Exception as e:
                print(f"[CLI][ERROR] 处理命令异常: {e}")
                import traceback

                traceback.print_exc()
                continue
            if response["type"] == "error":
                print("请重试。")
