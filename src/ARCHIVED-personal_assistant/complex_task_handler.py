from src.personal_assistant.secretary import Secretary
from src.personal_assistant.planner import Planner
from src.personal_assistant.task_manager import TaskManager
from src.personal_assistant.executor import Executor

class ComplexTaskHandler:
    def __init__(self, secretary=None, planner=None, task_manager=None, executor=None, api_list=None):
        self.secretary = secretary or Secretary()
        self.planner = planner or Planner()
        self.task_manager = task_manager or TaskManager()
        self.executor = executor or Executor()
        self.api_list = api_list or []

    def handle(self, history: list[str], user_input: str):
        refined_task = self.secretary.refine(history, user_input)
        plan = self.planner.plan(refined_task, self.api_list)
        task_id = self.task_manager.create_task(plan)
        self.executor.execute_plan_async(task_id)
